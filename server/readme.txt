GameServer handles connections and dispatches messages.

GameRoom handles players grouped into matches and calls Game methods to update logic.

Game handles core game mechanics and logic, independent of networking.


GameServer Class
    Purpose

        Manages:

        WebSocket connections.

        Creation and destruction of game rooms.

        Message routing between players and rooms.

        Global server state (list of all connected players, rooms).

        Key Responsibilities

        Accept new connections and assign players to rooms.

        Handle disconnections and clean up resources.

        Route messages (e.g., movement, shooting) to appropriate GameRoom.

        Broadcast server-level notifications (e.g., server shutdown).

    Key Methods

        start_server(host, port): Starts the WebSocket server.

        handle_client(websocket, path): Handles incoming client connections and requests.

        create_room(max_players): Creates a new game room.

        assign_player_to_room(player_info): Finds or creates a suitable room for the player.

        remove_player_from_room(player_id): Handles player disconnections.

        broadcast_global(message): Sends a message to all connected clients.

        tick(): Runs the main server loop, calling each room’s tick() for updates.

2. GameRoom Class
    Purpose

        Represents an individual game session. It stores:

        Players in the room.

        Current game status (waiting, in-progress, ended).

        Reference to a Game instance to handle game logic.

        Key Responsibilities

        Add/remove players.

        Assign teams (if applicable).

        Broadcast messages within the room.

        Start, end, and reset games.

    Key Methods

        add_player(ws, player_info): Adds a player to the room.

        remove_player(ws): Removes a disconnected player.

        broadcast(message, exclude_ws=None): Sends a message to all players in the room.

        broadcast_game_state(game_state): Sends the current game state to all players.

        find_player_by_id(player_id): Retrieves player details by ID.

        assign_team(player_id): Assigns the player to a team (optional).

        start_game(): Initializes the Game instance and starts the match.

        end_game(): Ends the game and updates results.

        reset_room(): Clears room data for reuse.

        tick(): Updates the game state by calling Game.tick().

        send_private_message(player_id, message): Sends a message to a single player.

        broadcast_except(exclude_id, message): Sends a message to everyone except one player.

        log_event(event_type, details): Logs events for debugging or analytics.

3. Game Class
    Purpose

        Handles game mechanics and logic independently of networking.

        Key Responsibilities

        Maintain all in-game entities (players, bullets, enemies).

        Process player inputs (movement, actions).

        Detect collisions (e.g., bullet hits enemy).

        Calculate scores and determine game outcomes.

    Key Methods

        initialize_game(settings): Sets up the initial state (map, entities, etc.).

        process_input(player_id, input_data): Updates player actions like movement and shooting.

        update(delta_time): Runs the core game loop logic each tick (physics, AI, etc.).

        detect_collisions(): Checks for bullet-enemy or player-enemy collisions.

        handle_scoring(player_id): Updates scores based on game events.

        is_game_over(): Checks if game conditions are met (time limit, score limit, etc.).

        get_game_state(): Returns the current game state for broadcasting.

        reset(): Resets the game for a new round.

Usage Flow

    Player connects:
    GameServer assigns them to a GameRoom.

    Room reaches capacity:
    GameRoom.start_game() initializes a Game instance.

    During gameplay:

    Players send input (movement/shooting) to the server.

    GameRoom forwards input to Game.

    Game updates the state and returns the new game state.

    GameRoom broadcasts updated state to all players.

    Game ends:
    GameRoom.end_game() is called, and results are sent to players.