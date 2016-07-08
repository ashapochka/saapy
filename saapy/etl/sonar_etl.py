class SonarETL:
    def __init__(self, sonar):
        self.sonar = sonar

    def export_dups(self, keys):
        sonar_dups = {}
        for k in keys:
            dups = self.sonar.get("api/duplications/show", dict(key=k))
            sonar_dups[k] = dups
        return sonar_dups
