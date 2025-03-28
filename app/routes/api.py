from flask import Blueprint, request, jsonify, current_app
from app.models.user import User
from app import cache, limiter
from chessdotcom import get_player_profile, get_player_stats, get_player_game_archives, get_player_games_by_month_pgn, Client
import google.generativeai as genai
from config import Config
import logging

bp = Blueprint('api', __name__, url_prefix='/api')

Client.request_config["headers"]["User-Agent"] = (
    "Chess Style Analysis API "
    "Contact: example@chess.com"
)

def verify_api_key():
    # More detailed API key verification
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        current_app.logger.warning(f"No API key provided for {request.path}")
        return None
    
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        current_app.logger.warning(f"Invalid API key used: {api_key}")
    return user

@bp.before_request
def before_request():
    # Detailed logging for incoming requests
    current_app.logger.info(f"Incoming {request.method} request to {request.path}")
    current_app.logger.info(f"Headers: {request.headers}")
    
    # Allow OPTIONS requests to pass through
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    user = verify_api_key()
    if not user:
        current_app.logger.error(f"API key verification failed for {request.path}")
        return jsonify({'error': 'Invalid or missing API key'}), 401

@bp.route('/player/profile/<username>', methods=['GET'])
@limiter.limit("100/day")
@cache.memoize(timeout=300)
def get_player_profile_route(username):
    try:
        current_app.logger.info(f"Fetching profile for username: {username}")
        data = get_player_profile(username).json
        stats = get_player_stats(username).json
        
        profile = data['player']
        profile['stats'] = stats
        
        return jsonify(profile), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching player profile: {str(e)}")
        return jsonify({'error': str(e)}), 400

@bp.route('/player/style/<username>', methods=['GET'])
@limiter.limit("50/day")
@cache.memoize(timeout=600)
def get_play_style_prompt(username):
    try:
        # Initialize Gemini AI
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        model = genai.GenerativeModel(
            'models/gemini-1.5-flash',
            system_instruction="Concisely analyze a chess player's style from their game history."
        )
        
        # Get most recent games archive
        archives = get_player_game_archives(username).json['archives']
        recent_archive = archives[-1]  # Most recent month
        
        # Extract recent games
        year = recent_archive[-7:-3]
        month = recent_archive[-2:]
        games = get_player_games_by_month_pgn(username, year, month).text[:20000]  # Limit to 20,000 chars
        
        # Generate compact style analysis
        style_analysis = model.generate_content(
            f'Provide a brief, focused 3-paragraph analysis of {username}\'s chess playing style. '
            'Cover key characteristics like opening preferences, tactical approach, '
            'and strategic strengths/weaknesses. Be precise and use specific examples.'
        )
        
        return jsonify({
            'username': username,
            'style_analysis': style_analysis.text,
            'games_period': f'{month}/{year}'
        }), 200
    except Exception as e:
        current_app.logger.error(f"Style analysis error for {username}: {str(e)}")
        return jsonify({'error': str(e)}), 400