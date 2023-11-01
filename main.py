from neo4j import GraphDatabase

class Player:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_player(self, player_name):
        with self._driver.session() as session:
            session.write_transaction(self._create_player, player_name)

    def update_player(self, player_id, new_name):
        with self._driver.session() as session:
            session.write_transaction(self._update_player, player_id, new_name)

    def delete_player(self, player_id):
        with self._driver.session() as session:
            session.write_transaction(self._delete_player, player_id)

    @staticmethod
    def _create_player(tx, player_name):
        query = "CREATE (p:Player {name: $player_name}) RETURN id(p)"
        result = tx.run(query, player_name=player_name)
        return result.single()[0]

    @staticmethod
    def _update_player(tx, player_id, new_name):
        query = "MATCH (p:Player) WHERE id(p) = $player_id SET p.name = $new_name"
        tx.run(query, player_id=player_id, new_name=new_name)

    @staticmethod
    def _delete_player(tx, player_id):
        query = "MATCH (p:Player) WHERE id(p) = $player_id DETACH DELETE p"
        tx.run(query, player_id=player_id)

class Match:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_match(self, result, players):
        with self._driver.session() as session:
            return session.write_transaction(self._create_match, result, players)

    def get_match_info(self, match_id):
        with self._driver.session() as session:
            return session.read_transaction(self._get_match_info, match_id)

    @staticmethod
    def _create_match(tx, result, players):
        query = (
            "CREATE (m:Match {result: $result}) "
            "WITH m "
            "UNWIND $players AS player_id "
            "MATCH (p:Player) WHERE id(p) = player_id "
            "CREATE (p)-[:PARTICIPATED_IN]->(m)"
        )
        tx.run(query, result=result, players=players)

    @staticmethod
    def _get_match_info(tx, match_id):
        query = "MATCH (m:Match) WHERE id(m) = $match_id RETURN m.result"
        result = tx.run(query, match_id=match_id)
        return result.single()[0]

# Exemplo de uso:
if __name__ == "__main__":
    player_db = Player("bolt://54.175.172.207:7687", "neo4j", "rifling-vendors-inventions")
    match_db = Match("bolt://54.175.172.207:7687", "neo4j", "rifling-vendors-inventions")

    # Criar jogador
    player_db.create_player("Player 1")

    # Criar partida e registrar resultados
    player1 = player_db.create_player("Player 1")
    player2 = player_db.create_player("Player 2")
    match_result = "Player 1 wins"
    players = [player1, player2]
    match_db.create_match(match_result, players)

    # Obter informações sobre uma partida
    match_info = match_db.get_match_info(1)
    print(f"Resultado da partida: {match_info}")

    player_db.close()
    match_db.close()