import pprint

from database.tables import create_database, get_session
from parser import Parser
from injester import insert_data
from model import model_main
import awpy

def main():

    sess = databse_controller()
    
    model_main.controller(sess)

def databse_controller():
    engine = create_database("sqlite:///test.db")
    session = get_session(engine)

    return session


def parse():
    d = Parser("dem/parivision-vs-nemiga-m1-mirage.dem")

    d.parse_dem()
    r = d.rounds()
    print(d.map_name)
    d.get_dataFrames(r)



if __name__ == '__main__':
    main()