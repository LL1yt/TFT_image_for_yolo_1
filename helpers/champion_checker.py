class ChampionChecker:
    @staticmethod
    def is_champion_missing(detected_champion_names, champion_coordinates):
        for champ_name in detected_champion_names:
            if champ_name not in champion_coordinates:
                return True
        return False


# Ожидаемый результат: True, т.к. "Akali" отсутствует в словаре
