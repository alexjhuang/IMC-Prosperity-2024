import random
from collections import defaultdict

class Cell:
    def __init__(self, hunters, value) -> None:
        self.hunters = hunters
        self.flat_value = value
        self.value = value * 7500
        self.percentage_agents = 0
        self.probability = 1
        self.intelligent_probability = 1
    
    def getValue(self):
        return self.value / self.hunters
    
    def getIntelligentValue(self):
        return self.value / (self.hunters + self.percentage_agents)
    
    def process(self, times_chosen, n):
        # update cell's probability based on it's value
        self.percentage_agents = (times_chosen / n) * 100
        self.probability = self.getValue()
        self.intelligent_probability = self.getIntelligentValue()


class Agent:
    def __init__(self, id) -> None:
        # set random seed
        random.seed(id)

    def chooseCell(self, cells):
        # randomly choose three cells based off of their probability attribute
        return random.choices(cells, weights=[cell.probability for cell in cells], k=3)
        
class IntelligentAgent(Agent):
    def chooseCell(self, cells):
        # k = 2 if no cells above intelligent value 75000
        if all(cell.getIntelligentValue() < 75000 for cell in cells):
            return random.choices(cells, weights=[cell.intelligent_probability for cell in cells], k=2)
        # randomly choose three cells based off of their probability attribute
        return random.choices(cells, weights=[cell.intelligent_probability for cell in cells], k=3)
    

cycles = 5
# create 5000 agents and 5000 intelligent agents each with a radom seed
dumb_agents = [Agent(random.randint(1, 5000)) for i in range(5000)]
intelligent_agents = [IntelligentAgent(random.randint(1, 8000)) for i in range(5000)]
#combine agents
agents = dumb_agents + intelligent_agents

#create board
cells = [
    Cell(2, 24),
    Cell(4, 70),
    Cell(3, 41),
    Cell(2, 21),
    Cell(4, 60),
    Cell(3, 47),
    Cell(5, 82),
    Cell(5, 87),
    Cell(5, 80),
    Cell(3, 35),
    Cell(4, 73),
    Cell(5, 89),
    Cell(8, 100),
    Cell(7, 90),
    Cell(2, 17),
    Cell(5, 77),
    Cell(5, 83),
    Cell(5, 85),
    Cell(5, 79),
    Cell(4, 55),
    Cell(2, 12),
    Cell(3, 27),
    Cell(4, 52),
    Cell(2, 15),
    Cell(3, 30)
         ]

for i in range(cycles):
    all_choices = defaultdict(int) # {cell: number of times chosen
    for agent in agents:
        choices = agent.chooseCell(cells)
        for choice in choices:
            all_choices[choice] += 1

    #update cells
    for cell in cells:
        cell.process(all_choices[cell], len(agents))


# sort the cells by the highest intelligent values
cells.sort(key=lambda x: x.intelligent_probability, reverse=True)
for i in range(5):
    print("CELL ID", cells[i].flat_value, cells[i].hunters)
    print(cells[i].percentage_agents)
    print(cells[i].getIntelligentValue())
