from openreward.environments import Server
from env import CountdownEnvironment

if __name__ == "__main__":
    server = Server([CountdownEnvironment])
    server.run()
