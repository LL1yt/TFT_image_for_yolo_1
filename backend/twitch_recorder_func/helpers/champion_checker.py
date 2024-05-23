class ChampionChecker:
    @staticmethod
    def is_champion_missing(detected_champion_names, champion_coordinates):
        for champ_name in detected_champion_names:
            if champ_name not in champion_coordinates:
                return True
        return False

    @staticmethod
    def add_missing_champions(detected_champion_names, champion_coordinates):
        for champ_name in champion_coordinates.keys():
            if champ_name not in detected_champion_names:
                detected_champion_names.append(champ_name)
        return detected_champion_names
