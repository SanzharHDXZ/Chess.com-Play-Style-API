from flask import Blueprint, request, jsonify
from app.models.user import User
from app import cache, limiter
from chessdotcom import get_player_profile, get_player_stats, get_player_game_archives, get_player_games_by_month_pgn, Client
import google.generativeai as genai
from config import Config

bp = Blueprint('api', __name__, url_prefix='/api')

Client.request_config["headers"]["User-Agent"] = (
    "Chess Style Analysis API"
    "Contact: example@chess.com"
)

def verify_api_key():
    # Skip API key verification for OPTIONS requests
    if request.method == 'OPTIONS':
        return True
        
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return None
    return User.query.filter_by(api_key=api_key).first()

@bp.before_request
def before_request():
    # Allow OPTIONS requests to pass through
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    if not verify_api_key():
        return jsonify({'error': 'Invalid API key'}), 401

@bp.route('/player/profile/<username>', methods=['GET'])
@limiter.limit("100/day")
@cache.memoize(timeout=300)
def get_player_profile_route(username):
    try:
        data = get_player_profile(username).json
        stats = get_player_stats(username).json
        
        profile = data['player']
        profile['stats'] = stats
        
        return jsonify(profile), 200
    except Exception as e:
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
            system_instruction="You are a chess expert! Analyze player's chess games and provide detailed style analysis."
        )
        
        # Get recent games
        archives = get_player_game_archives(username).json['archives'][-3:]  # Last 6 months
        games_history = []
        
        for archive in archives:
            year = archive[-7:-3]
            month = archive[-2:]
            games = get_player_games_by_month_pgn(username, year, month).text
            games_history.append(games[:30000])  # Limit to 30,000 characters

        # Generate analysis for each month
        game_summaries = []
        for games in games_history:
            response = model.generate_content(
                f'Provide a summary of {username}\'s playing style based on these games: {games}'
            )
            game_summaries.append(response.text)
        
        # Generate overall analysis
        final_analysis = model.generate_content(
            f'Provide a comprehensive analysis of {username}\'s playing style based on these summaries: {game_summaries}'
        )
        
        return jsonify({
            'username': username,
            'style_analysis': final_analysis.text,
            'monthly_summaries': game_summaries
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
if __name__ == "__main__":
    from flask import Flask
    from config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    from app import cache, limiter
    cache.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(bp)

    app.run(host="0.0.0.0", port=10000)

