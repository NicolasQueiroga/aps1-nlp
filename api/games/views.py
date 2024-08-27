import html
import re
from time import sleep
import requests
from datetime import datetime
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import GameSerializer
from .models import Game


def parse_date(date_str):
    date_formats = ["%b %d, %Y", "%d %b, %Y"]

    for date_format in date_formats:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            continue

    raise ValueError(f"Date format for '{date_str}' not recognized.")


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def get_queryset(self, limit=10):
        queryset = super().get_queryset()

        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return queryset

        param_limit = self.request.query_params.get("limit", None)
        if param_limit and int(param_limit) > 0:
            queryset = queryset[: int(param_limit)]
        elif limit != -1:
            queryset = queryset[:limit]

        return queryset

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="fetch-games",
    )
    def fetch_games_from_steam(self, request):
        response = requests.get(
            "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        )
        games_ids = response.json()["applist"]["apps"]

        for game in games_ids:
            appid = game["appid"]
            response = requests.get(
                f"https://store.steampowered.com/api/appdetails?appids={appid}"
            )
            data = response.json()
            if appid and data is not None:
                if data[str(appid)]["success"]:
                    game_data = data[str(appid)]["data"]
                    if not Game.objects.filter(appid=game_data["steam_appid"]).exists():
                        try:
                            raw_description = game_data["detailed_description"].replace(
                                "<br>", "\n"
                            )
                            cleaned_description = re.sub("<.*?>", "", raw_description)
                            final_description = html.unescape(cleaned_description)
                            Game.objects.create(
                                appid=game_data["steam_appid"],
                                name=game_data["name"],
                                is_free=game_data["is_free"],
                                description=final_description,
                                categories=[
                                    cat["description"]
                                    for cat in game_data["categories"]
                                ],
                                genres=[
                                    genre["description"]
                                    for genre in game_data["genres"]
                                ],
                                release_date=parse_date(
                                    game_data["release_date"]["date"]
                                ).strftime("%Y-%m-%d"),
                            )
                        except Exception as e:
                            print(e)
                    else:
                        try:
                            raw_description = game_data["detailed_description"].replace(
                                "<br>", "\n"
                            )
                            cleaned_description = re.sub("<.*?>", "", raw_description)
                            final_description = html.unescape(cleaned_description)
                            game = Game.objects.get(appid=game_data["steam_appid"])
                            game.name = game_data["name"]
                            game.is_free = game_data["is_free"]
                            game.description = final_description
                            game.categories = [
                                cat["description"] for cat in game_data["categories"]
                            ]
                            game.genres = [
                                genre["description"] for genre in game_data["genres"]
                            ]
                            game.release_date = parse_date(
                                game_data["release_date"]["date"]
                            ).strftime("%Y-%m-%d")
                            game.save()
                        except Exception as e:
                            print(e)
                    sleep(0.1)

        return Response("Games fetched successfully")

    @action(
        detail=False,
        methods=["get"],
        url_path="games-count",
    )
    def games_count(self, request):
        return Response(Game.objects.count())
