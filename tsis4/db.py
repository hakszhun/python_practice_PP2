import psycopg2
from psycopg2 import sql
from datetime import datetime
import config

class Database:
    def __init__(self):
        self.conn = None
        self.connect()
        self.init_tables()
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            self.conn.autocommit = True
            print("Connected to PostgreSQL successfully!")
        except Exception as e:
            print(f"Database connection error: {e}")
    
    def init_tables(self):
        try:
            cursor = self.conn.cursor()
            
            # Create players table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                )
            """)
            
            # Create game_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id),
                    score INTEGER NOT NULL,
                    level_reached INTEGER NOT NULL,
                    played_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            cursor.close()
            print("Tables initialized successfully!")
        except Exception as e:
            print(f"Table initialization error: {e}")
    
    def get_or_create_player(self, username):
        try:
            cursor = self.conn.cursor()
            
            # Check if player exists
            cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
            result = cursor.fetchone()
            
            if result:
                player_id = result[0]
            else:
                # Create new player
                cursor.execute(
                    "INSERT INTO players (username) VALUES (%s) RETURNING id",
                    (username,)
                )
                player_id = cursor.fetchone()[0]
            
            cursor.close()
            return player_id
        except Exception as e:
            print(f"Error getting/creating player: {e}")
            return None
    
    def save_game_result(self, username, score, level_reached):
        try:
            player_id = self.get_or_create_player(username)
            if player_id:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO game_sessions (player_id, score, level_reached, played_at)
                    VALUES (%s, %s, %s, %s)
                """, (player_id, score, level_reached, datetime.now()))
                cursor.close()
                return True
        except Exception as e:
            print(f"Error saving game result: {e}")
        return False
    
    def get_leaderboard(self, limit=10):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT p.username, gs.score, gs.level_reached, 
                       TO_CHAR(gs.played_at, 'YYYY-MM-DD HH24:MI') as played_at
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                ORDER BY gs.score DESC
                LIMIT %s
            """, (limit,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    def get_personal_best(self, username):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT MAX(gs.score) as best_score
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                WHERE p.username = %s
            """, (username,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result and result[0] else 0
        except Exception as e:
            print(f"Error getting personal best: {e}")
            return 0
    
    def close(self):
        if self.conn:
            self.conn.close()