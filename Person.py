CPF_MASK = "{}{}{}.{}{}{}.{}{}{}-{}{}"
CEL_MASK = "({}{}) {}{}{}{}-{}{}{}{}"
CARD_MASK = "{}{}{}{} {}{}{}{} {}{}{}{} {}{}{}{}"

class Person():
    def __init__(self):
        self.name = ""
        self.sex = ""
        self.address = ""
        self.city = ""
        self.uf = ""
        self.cpf = ""
        self.cel = ""
        self.bDay = None
        self.email = ""
        self.cardCompany = ""
        self.cardNumber = ""
        self.cardVigor = ""
        self.cardLimit = ""
        self.cvc2 = 0
        self.height = 0.
        self.weigh = 0.
        self.tBlood = ""
        self.guid = ""
    

    def __str__(self):
        value = ""
        value += "nome      : " + self.name + "\n"
        value += "sexo      : " + self.sex + "\n"
        value += "endereço  : " + self.address + "\n"
        value += "cidade    : " + self.city + "\n"
        value += "uf        : " + self.uf + "\n"
        value += "cpf       : " + CPF_MASK.format(*self.cpf) + "\n"
        value += "celular   : " + CEL_MASK.format(*self.cel) + "\n"
        value += "bDay      : " + self.bDay.strftime('%d/%m/%Y') + "\n"
        value += "email     : " + self.email + "\n"
        value += "Emp Cartão: " + self.cardCompany + "\n"
        value += "nº cartão : " + CARD_MASK.format(*self.cardNumber) + "\n"
        value += "cvc2      : " + str(self.cvc2) + "\n"
        value += "validade  : " + self.cardVigor.strftime('%d/%m/%Y') + "\n"
        value += "limite    : " + str(self.cardLimit) + "\n"
        value += "altura    : " + str(self.height) + "\n"
        value += "peso      : " + str(self.weigh) + "\n"
        value += "sangue    : " + self.tBlood + "\n"
        value += "GUID      : " + self.guid

        return value


    def toDict(self):
        return {
            "_id": self.cpf,
            "guid": self.guid,
            "nome": self.name,
            "bDay": self.bDay,
            "fisico": {
                "sexo": self.sex,
                "altura": self.height,
                "peso": self.weigh,
                "sangue": self.tBlood
            },
            "endereco": {
                "rua_n": self.address,
                "cidade": self.city,
                "uf": self.uf
            },
            "comunicacao": {
                "celular": self.cel,
                "email": self.email,
                "cartao": {
                    "empresa": self.cardCompany,
                    "numero": self.cardNumber,
                    "cvc2": self.cvc2,
                    "validade": self.cardVigor,
                    "limite": self.cardLimit
                }
            }
        }