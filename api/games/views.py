import html
import re
from time import sleep
import requests
from datetime import datetime
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import GameSerializer
from .models import Game


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

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
        url_path="games-count",
    )
    def games_count(self, request):
        return Response(Game.objects.count())

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
                    print(f"Fetching game with appid: {appid}")
                    self.game_data = data[str(appid)]["data"]
                    try:
                        raw_description = self.game_data[
                            "detailed_description"
                        ].replace("<br>", "\n")
                        cleaned_description = re.sub("<.*?>", "", raw_description)

                        name = self.game_data["name"]
                        is_free = self.game_data["is_free"]
                        detailed_description = html.unescape(cleaned_description)
                        categories = [
                            cat["description"] for cat in self.game_data["categories"]
                        ]
                        genres = [
                            genre["description"] for genre in self.game_data["genres"]
                        ]
                        release_date = self._parse_date(
                            self.game_data["release_date"]["date"]
                        ).strftime("%Y-%m-%d")

                        today = datetime.today().date()
                        date_obj = datetime.strptime(release_date, "%Y-%m-%d").date()
                        game_age = (today - date_obj).days
                        game_age_category = "new" if game_age < 365 else "old"

                        content = f"{name} {'free' if is_free else 'paid'} {game_age_category} {' '.join(categories)} {' '.join(genres)} {detailed_description}"
                    except Exception as e:
                        print(f"Error extracting game content: {e}")
                        continue

                    if not Game.objects.filter(appid=appid).exists():
                        Game.objects.create(
                            appid=appid,
                            name=name,
                            is_free=is_free,
                            description=detailed_description,
                            categories=categories,
                            genres=genres,
                            content=content,
                        )
                    else:
                        game = Game.objects.get(appid=appid)
                        game.name = name
                        game.is_free = is_free
                        game.description = detailed_description
                        game.categories = categories
                        game.genres = genres
                        game.content = content
                        game.save()

                    sleep(0.1)

        return Response("Games fetched successfully")

    def _parse_date(self, date_str):
        date_formats = ["%b %d, %Y", "%d %b, %Y"]
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue

        raise ValueError(f"Date format for '{date_str}' not recognized.")
