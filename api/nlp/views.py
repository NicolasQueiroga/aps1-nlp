from rest_framework.decorators import api_view
from rest_framework.response import Response
from games.serializers import GameSerializer
from games.models import Game
from .nlp.tf_idf import TFIDF


@api_view(["GET"])
def query(request):
    query = request.query_params.get("query")
    nlp_model = request.query_params.get("model")

    games = Game.objects.exclude(content="")

    if nlp_model == "tfidf" or True:
        corpus = [(game.appid, game.content) for game in games]
        tfidf = TFIDF(corpus)
        tfidf.fit_transform()
        appid_list, similarity_list = zip(
            *tfidf.get_similar_games(query, threshold=0.10)
        )
        similarity_map = dict(zip(appid_list, similarity_list))
        queryset = Game.objects.filter(appid__in=similarity_map.keys())

        sorted_games = sorted(
            queryset, key=lambda game: similarity_map.get(game.appid, 0.0), reverse=True
        )

        serializer = GameSerializer(
            sorted_games, many=True, context={"similarity_map": similarity_map}
        )

        return Response(serializer.data)

    return Response([])
