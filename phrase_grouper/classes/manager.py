from classes import data, models

class Config:
    def __init__(self):
        self.book_name = 'Salaries'
        self.sheet_name = 'Transparency'
        self.categories_raw = '''
        accounting banking Finance insurance real estate 
        advertising Consulting marketing 
        automotive aviation logistics transportation 
        Construction energy engineering manufacturing supply chain
        cyber fintech software technology tech telecommunication
        Education
        entertainment food hospitality restaurant Retail 
        Government public federal
        healthcare medical pharmaceutical
        Legal law
        Nonprofit non profit
        '''.strip().split('\n')

class Manager:
    def __init__(self):
        self.config = Config()
        self.config.categories_raw = [category.strip() for category in self.config.categories_raw]
        self.config.vectoriser = models.Vectoriser(config_ = self.config)
    def read_dfs(self):
        self.config.industries = data.Industries(config_ = self.config)
        self.config.industries.main()
        self.config.categories = data.Categories(config_ = self.config)
        self.config.categories.main()
    def calculate(self):
        self.config.metrics = models.Metrics(config_ = self.config)
        self.config.metrics.main()
        self.config.cluster = models.Cluster(config_ = self.config)
        self.config.cluster.main()
    def output_df(self):
        self.output = data.Output(config_ = self.config)
        self.output.main()
    def main(self):
        self.read_dfs()
        self.calculate()
        self.output_df()
