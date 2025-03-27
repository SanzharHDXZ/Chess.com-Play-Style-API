from flask import Blueprint, request, jsonify
from app.models.user import User
from app import cache, limiter
from chessdotcom import get_player_profile, get_player_stats, get_player_game_archives, get_player_games_by_month_pgn, Client
import google.generativeai as genai
from config import Config
import logging

bp = Blueprint('api', __name__, url_prefix='/api')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redacted User-Agent configuration
Client.request_config["headers"]["User-Agent"] = "Chess Style Analysis API"

def verify_api_key():
    """Verify the API key for incoming requests."""
    if request.method == 'OPTIONS':
        return True
        
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        logger.warning("No API key provided")
        return None
    
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        logger.warning("Invalid API key attempted")
        return None
    
    return user

@bp.before_request
def before_request():
    """Middleware to check API key before processing requests."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    if not verify_api_key():
        return jsonify({'error': 'Invalid API key'}), 401

@bp.route('/player/profile/<username>', methods=['GET'])
@limiter.limit("100/day")
@cache.memoize(timeout=300)
def get_player_profile_route(username):
    """Retrieve player profile and statistics."""
    try:
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        data = get_player_profile(username).json
        stats = get_player_stats(username).json
        
        profile = data['player']
        profile['stats'] = stats
        
        return jsonify(profile), 200
    except Exception as e:
        logger.error(f"Profile retrieval error for {username}: {str(e)}")
        return jsonify({'error': 'Unable to retrieve player profile'}), 500

@bp.route('/player/style/<username>', methods=['GET'])
@limiter.limit("50/day")
@cache.memoize(timeout=600)
def get_play_style_prompt(username):
    """Analyze player's chess playing style."""
    try:
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # Validate API key configuration
        if not Config.GOOGLE_API_KEY:
            logger.error("Google API key not configured")
            return jsonify({'error': 'AI analysis service unavailable'}), 500

        # Initialize Generative AI
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        model = genai.GenerativeModel(
            'models/gemini-1.5-flash',
            system_instruction="You are a chess expert! Analyze player's chess games and provide detailed style analysis."
        )
        
        # Fetch game archives
        try:
            archives = get_player_game_archives(username).json['archives'][-3:]
        except Exception as arch_error:
            logger.error(f"Game archives retrieval error: {str(arch_error)}")
            return jsonify({'error': 'Unable to retrieve game history'}), 404

        # Collect game history
        games_history = []
        for archive in archives:
            year = archive[-7:-3]
            month = archive[-2:]
            try:
                games = get_player_games_by_month_pgn(username, year, month).text
                games_history.append(games[:30000])  # Limit to 30,000 characters
            except Exception as games_error:
                logger.warning(f"Error retrieving games for {username} in {year}-{month}")

        # Validate game history
        if not games_history:
            return jsonify({'error': 'No game history available'}), 404

        # Generate analysis
        game_summaries = []
        for games in games_history:
            try:
                response = model.generate_content(
                    f'Provide a summary of {username}\'s playing style based on these games: {games}'
                )
                game_summaries.append(response.text)
            except Exception as gen_error:
                logger.error(f"AI analysis error: {str(gen_error)}")

        # Generate comprehensive analysis
        try:
            final_analysis = model.generate_content(
                f'Provide a comprehensive analysis of {username}\'s playing style based on these summaries: {game_summaries}'
            )
        except Exception as final_error:
            logger.error(f"Final analysis generation error: {str(final_error)}")
            return jsonify({'error': 'Unable to complete style analysis'}), 500
        
        return jsonify({
            'username': username,
            'style_analysis': final_analysis.text,
            'monthly_summaries': game_summaries
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error in play style analysis: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500