import streamlit as st
import random
import time
import uuid

st.set_page_config(page_title="DUODLE", layout="wide")
st.title("DUODLE: Wordle, but together <3")

WORD_LIST = [
    "JOURNEY", "PROMISE", "STATION", "WEATHER", "FREEDOM", "SILENCE", "KITCHEN", "VICTORY", 
    "BLANKET", "MONSTER", "CAPTAIN", "HAMBURGER", "FEATHER", "DIAMOND", "CRYSTAL", "ACCOUNT", 
    "AGAINST", "ALREADY", "ANOTHER", "ARRANGE", "BATTERY", "BICYCLE", "BRAVERY", "BREATHS", 
    "BUFFALO", "CABINET", "CALCIUM", "CAMERAS", "CHALLEN", "CHAMPON", "CHANNEL", "CHARGER", 
    "CHARITY", "CHEETAH", "CHICKEN", "CHIMNEY", "COLLEGE", "COMFORT", "COMPANY", "CONCERT", 
    "COUNTRY", "COURAGE", "CULTURE", "CURTAIN", "DAYTIME", "DEFENSE", "DESKTOP", "DESTROY", 
    "DEVELOP", "DIGITAL", "DISCUSS", "DIVIDED", "DYNAMIC", "ELEMENT", "EMERALD", "EVENING", 
    "EXACTLY", "EXAMPLE", "EXCITED", "EXPLAIN", "FACTORY", "FESTIVE", "FINALLY", "FLAMINGO", 
    "FOREIGN", "FOREVER", "FORWARD", "GALAXY", "GARBAGE", "GARDENS", "GARMENT", "GATEWAY", 
    "GENTMAN", "GHOSTLY", "GLACIER", "GLIMPSE", "GLORIOUS", "GOGGLES", "GORILLA", "GRAVITY", 
    "GROCERY", "HALFWAY", "HANDFUL", "HARVEST", "HEALTHY", "HEAVILY", "HELPFUL", "HEROISM", 
    "HISTORY", "HOLIDAY", "HORIZON", "HUNGRY", "HURRYING", "ICEBERG", "ILLEGAL", "IMAGINE", 
    "IMPRESS", "IMPROVE", "IMPULSE", "INCLUDE"]

@st.cache_resource
def get_global_lobbies():
    return {}

lobbies = get_global_lobbies()

if "player_id" not in st.session_state:
    st.session_state.player_id = str(uuid.uuid4())[:6]
if "current_lobby" not in st.session_state:
    st.session_state.current_lobby = None

col1, col2 = st.columns(2)

with col1:
    st.subheader("Start a New Game")
    if st.button("Generate Game Code"):
        game_code = str(uuid.uuid4())[:6].upper()
        lobbies[game_code] = {
            "host": st.session_state.player_id,
            "guest": None,
            "status": "waiting",
            "word": random.choice(WORD_LIST),
            "guesses": [],
            "turn": "host",
            "start_time": None,
            "archive": [],
            "last_update": time.time()
        }
        st.session_state.current_lobby = game_code

with col2:
    st.subheader("Join a Game")
    join_code = st.text_input("Enter 6-digit Game Code:").upper().strip()
    if st.button("Join"):
        if join_code in lobbies:
            if lobbies[join_code]["host"] == st.session_state.player_id:
                st.warning("You are already the host of this game.")
            elif lobbies[join_code]["guest"] is not None and lobbies[join_code]["guest"] != st.session_state.player_id:
                st.error("Game is full!.")
            else:
                lobbies[join_code]["guest"] = st.session_state.player_id
                lobbies[join_code]["status"] = "ready"
                lobbies[join_code]["last_update"] = time.time()
                st.session_state.current_lobby = join_code
                st.success("Successfully joined the game!")
        else:
            st.error("Invalid Code.")

@st.fragment(run_every=2)
def game_loop(code):
    game = lobbies[code]
    role = "host" if game["host"] == st.session_state.player_id else "guest"
    
    st.markdown("---")
    st.info(f"**Game Code:** {code}")
    
    if game["status"] == "waiting":
        st.warning("Waiting for Player 2 to join...")
        
    elif game["status"] == "ready":
        if role == "host":
            st.write("Player 2 has joined!")
            if st.button("Start Game", type="primary"):
                game["status"] = "playing"
                game["start_time"] = time.time()
                game["last_update"] = time.time()
                st.rerun()
        else:
            st.warning("Waiting for the host to start the game...")
            
    elif game["status"] == "playing" or game["status"] == "game_over":
        elapsed = int(time.time() - game["start_time"]) if game["start_time"] else 0
        st.metric(label="YOU'VE SPENT:", value=f"{elapsed} seconds")
        st.write(f"Remaining Guesses: {8 - len(game['guesses'])} / 8")
        
        for g_num, (player_role, guess_word) in enumerate(game["guesses"]):
            cols = st.columns(7)
            target = game["word"]
            for idx in range(7):
                char = guess_word[idx]
                if target[idx] == char:
                    bg = "#6aaa64"
                elif char in target:
                    bg = "#c9b458"
                else:
                    bg = "#787c7e"
                cols[idx].markdown(f"<div style='background-color:{bg}; color:white; text-align:center; padding:15px; font-size:24px; font-weight:bold; border-radius:5px;'>{char}</div>", unsafe_allow_html=True)
        
        if game["status"] == "playing":
            is_my_turn = game["turn"] == role
            
            if is_my_turn:
                st.success("🟢 It is YOUR turn to guess!")
                user_guess = st.text_input("Type your 7-letter guess here:", max_chars=7, key="live_input").upper().strip()
                
                preview_cols = st.columns(7)
                for idx in range(7):
                    char_preview = user_guess[idx] if idx < len(user_guess) else ""
                    preview_cols[idx].markdown(f"<div style='border: 2px solid #bbb; color:black; text-align:center; padding:15px; font-size:24px; font-weight:bold; border-radius:5px; height:64px; background-color:white;'>{char_preview}</div>", unsafe_allow_html=True)
                
                if st.button("Submit Guess", type="primary"):
                    if len(user_guess) != 7:
                        st.error("Your guess must be exactly 7 letters long.")
                    else:
                        game["guesses"].append((role, user_guess))
                        if user_guess == game["word"] or len(game["guesses"]) >= 8:
                            game["status"] = "game_over"
                        else:
                            game["turn"] = "guest" if role == "host" else "host"
                        game["last_update"] = time.time()
                        st.rerun()
            else:
                st.warning(f"🔴 Waiting for Player 2 ({game['turn'].capitalize()}) to make a move...")
                preview_cols = st.columns(7)
                for idx in range(7):
                    preview_cols[idx].markdown(f"<div style='border: 2px dashed #ddd; padding:15px; height:64px; background-color:#fafafa;'></div>", unsafe_allow_html=True)
                
        elif game["status"] == "game_over":
            st.markdown("---")
            st.header("Summary")
            
            won = any(g[1] == game["word"] for g in game["guesses"])
            if won:
                st.success(f"🎉 You guessed the word! The word was **{game['word']}**.")
            else:
                st.error(f"❌ Out of guesses! The correct word was **{game['word']}**.")
                
            for i, (p_role, g_word) in enumerate(game["guesses"]):
                st.write(f"Guess {i+1} by **{p_role.capitalize()}**: `{g_word}`")
                
            if st.button("Generate next game!"):
                game["archive"].append({
                    "word": game["word"],
                    "guesses": game["guesses"].copy(),
                    "time_taken": elapsed,
                    "result": "Won" if won else "Lost"
                })
                game["word"] = random.choice(WORD_LIST)
                game["guesses"] = []
                game["turn"] = "host"
                game["start_time"] = time.time()
                game["status"] = "playing"
                game["last_update"] = time.time()
                st.rerun()
                
    if game["archive"]:
        st.markdown("---")
        with st.expander("View archive"):
            for idx, old_game in enumerate(game["archive"]):
                st.write(f"### Game #{idx+1} ({old_game['result']}) — Word: `{old_game['word']}`")
                st.write(f"* **Time Spent:** {old_game['time_taken']} seconds")
                st.write(f"* **Total Guesses:** {len(old_game['guesses'])}")
                st.markdown("---")

if st.session_state.current_lobby in lobbies:
    game_loop(st.session_state.current_lobby)