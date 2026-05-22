import random
import json
import ollama

def Ambiente(qttRoom: int) -> list[list[str, str]]:
    util = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o"]
    quartos = []
    for i in range(qttRoom):
        quartos.append([util[i], "s"])
    return quartos

class AgenteIA:
    def __init__(self, enviroment):#Inicialização do agente
        self.initialPos = random.choice(enviroment)[0]#Inicialmente, a posição onde o aspirador "nasce" é aleatório
        self.internalState = []
        for quarto in enviroment:
            self.internalState.append([quarto[0], "i"])

    def see(self, curState, enviroment) -> list[str, str]:#Sala que o agente está e situação da sala
        for quarto in enviroment:
            if curState[0] == quarto[0]:
                curState = quarto
        return curState

    def next(self, curState):#Atualiza estado interno
        for i in range (len(self.internalState)):
            if curState[0] == self.internalState[i][0]:
                self.internalState[i] = curState

    def action(self, curState, enviroment) -> list[str, str] | None:#Esquerda, Direita, Aspirar
        if not(any("s" in quarto[1] for quarto in self.internalState) or any("i" in quarto[1] for quarto in self.internalState)):
            print("Todos os quartos estão limpos!")
            print("Modo Descanso...")
            return None
        for i in range(len(enviroment)):
            if curState[0] == enviroment[i][0]:
                if enviroment[i][1] == "s":#Aspirar
                    print("Limpando o quarto...")
                    enviroment[i][1] = "l"
                    nextState = curState
                elif (self.internalState.index(curState)+1)<len(enviroment) and self.internalState[self.internalState.index(curState)+1][1] != "l":#Direita
                    print("Indo para o quarto à direita...")
                    nextState = self.internalState[self.internalState.index(curState)+1]
                else:#Esquerda
                    print("Indo para o quarto à esquerda...")
                    nextState = self.internalState[self.internalState.index(curState)-1]
                break
        return nextState
    
class AgenteIA_LLM:
    def __init__(self, enviroment):#Inicialização do agente
        self.initialPos = random.choice(enviroment)[0]#Inicialmente, a posição onde o aspirador "nasce" é aleatório
        self.internalState = []
        for quarto in enviroment:
            self.internalState.append([quarto[0], "i"])
    
    def promptAction(self, curState, enviroment):
        return f"""You are a cleaning robot in a house with {len(enviroment)} rooms. 
                \nYour current position is {curState[0]} and the state of the room is {'dirty' if curState[1] == 's' else 'clean'}. 
                \nYour internal state is {self.internalState}.
                \nNow, you need to decide what action to take next.
                \n\nThe possible actions are:
                \n***If the current room is dirty ('s')***
                \n  - CLEANING: If the room is dirty ('s'), change its state to 'l'(clean).
                \n***If the current room is clean ('l')***
                \n  - MOVE_LEFT: Move to the next room to the left if it's not clean.
                \n  - MOVE_RIGHT: Move to the next room to the right if it's not clean.
                \n\nThe output should be a list with 2 elements: 
                \n - [action, next_room], where:
                \n   - action: "CLEANING" or "MOVE_LEFT" or "MOVE_RIGHT" or None;
                \n   - next_room: [current_room, state], where:
                \n      - if action is "CLEANING", next_room should be the current room with its state updated to 'l'(clean), and NEVER RETURN THE SAME ROOM WITH THE SAME STATE 's'(dirty) OR 'i'(unknown);
                \n      - if action is "MOVE_LEFT" or "MOVE_RIGHT", next_room should be the room imediatally to the left or right of the current room, according to {self.internalState[self.internalState.index(curState)]} in {self.internalState}, with its state unchanged;
                \n      - ***YOU CAN JUST MOVE TO ADJACENT ROOMS! Available rooms: {self.internalState[self.internalState.index(curState)-1] if self.internalState.index(curState) > 0 else None} OR {self.internalState[self.internalState.index(curState)+1] if self.internalState.index(curState) < len(self.internalState) - 1 else None}, YOU CAN JUST MOVE TO THE ROOM AVAILABLE AND GIVE PREFERENCE TO THE ONE THAT IS NOT CLEAN***
                \n      - If both adjacent rooms are clean, you can choose either one.
                \nHere are some examples of the expected output:
                \n- Input: curState is ['a', 's']. Then the output should be: ['CLEANING', ['a', 'l']] (cleaning the current room);
                \n- Input: curState is ['a', 'l'] and the next room to the right is ['b', 'i']. Then the output should be: ['MOVE_RIGHT', ['b', 'i']] (moving to the next room);
                \n- Input: curState is ['b', 'l'] and the next room to the right is ['c', 'l']. Then the output should be: ['MOVE_LEFT', ['a', 'i']] (moving to the previous room);"""

    def see(self, curState, enviroment) -> list[str, str]:#Sala que o agente está e situação da sala
        for quarto in enviroment:
            if curState[0] == quarto[0]:
                curState = quarto
        return curState

    def next(self, curState):#Atualiza estado interno
        for i in range (len(self.internalState)):
            if curState[0] == self.internalState[i][0]:
                self.internalState[i] = curState

    def action(self, curState, enviroment) -> list[str, str] | None:

        if all(quarto[1] == 'l' for quarto in self.internalState):
            print("Todos os quartos estão limpos!")
            print("Modo Descanso...")
            return None

        schema = {
            "type": "array",
            "prefixItems": [
                {
                    "type": "string",
                    "enum": ["CLEANING", "MOVE_LEFT", "MOVE_RIGHT"]
                },
                {
                    "type": "array",
                    "prefixItems": [
                        {
                            "type": "string",
                            "enum": [quarto[0] for quarto in enviroment]
                        },
                        {
                            "type": "string",
                            "enum": ["i", "l", "s"]
                        }
                    ],
                    "minItems": 2,
                    "maxItems": 2
                }
            ],
            "minItems": 2,
            "maxItems": 2
        }

        response = ollama.chat(
            model="deepseek-r1:7b",
            messages=[
                {
                    "role": "system",
                    "content": self.promptAction(curState, enviroment)
                }
            ],
            format=schema,
            stream=False
        )

        response =json.loads(response['message']['content'])
        reasoning = response[0]
        formatted_response = response[1]

        if not(isinstance(formatted_response, list) and len(formatted_response) == 2):
            print("Received response from the model:", response['message']['content'])
            print("Invalid response from the model.")
            return None

        for i in range(len(enviroment)):
            if curState[0] == enviroment[i][0] and formatted_response[0] == curState[0]:
                enviroment[i][1] = formatted_response[1]
                break

        print("Reasoning: ", reasoning)
        print("Model's action:", formatted_response)

        return formatted_response

def main():
    qtdQuartos = int(input("Quantidade de Quartos: "))
    env = Ambiente(qtdQuartos)
    # aspirador = AgenteIA(env)
    aspirador = AgenteIA_LLM(env)
    curState = (aspirador.initialPos, "i")
    while(True):
        print("\n========== Percepção ==========\n")
        curState = aspirador.see(curState, env)
        print(curState)
        print("\n========== Estado Interno ==========\n")
        aspirador.next(curState)
        print(aspirador.internalState)
        print("\n========== Ação ==========\n")
        curState = aspirador.action(curState, env)
        if not curState:
            break

if __name__ == "__main__":
    main()