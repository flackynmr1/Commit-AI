def make_business_script(idea: str) -> str:
    idea = idea.strip()

    if not idea:
        idea = "en smart business-idé"

    script = f"""
Här är en enkel förklaring av affärsidén.

Problemet är att många människor vill lösa ett behov snabbt, men de orkar inte leta runt, jämföra alternativ eller lägga massa tid.

Idén är: {idea}

Lösningen är att skapa en enkel tjänst som gör processen snabbare, billigare och enklare för kunden.

Så här funkar det:
Först kommer kunden in på hemsidan eller appen.
Sedan väljer kunden vad den behöver hjälp med.
Efter det får kunden ett snabbt förslag, pris eller nästa steg.
Till sist kan kunden boka, köpa eller skicka en förfrågan direkt.

Det smarta med idén är att den kan automatiseras.
AI kan skriva svar, sortera leads, skapa offerter och hjälpa kunden dygnet runt.

Man kan tjäna pengar genom abonnemang, engångsbetalningar, provision eller premium-funktioner.

Målgruppen är personer eller företag som vill spara tid och få hjälp snabbare.

Det första steget är att bygga en enkel MVP:
En landningssida, ett formulär, en tydlig tjänst och en enkel betalning eller bokningsknapp.

Om folk börjar använda tjänsten kan man sedan lägga till mer automation, fler funktioner och bättre marknadsföring.

Det här är en affärsidé som kan startas enkelt, testas billigt och växa steg för steg.
"""
    return " ".join(script.split())


def make_short_script(idea: str) -> str:
    return f"""
Affärsidén är {idea}.
Den löser ett tydligt problem för kunder som vill spara tid.
Lösningen är en enkel digital tjänst där kunden snabbt kan få hjälp, boka eller köpa.
AI kan automatisera svar, offerter och kundkontakt.
Man kan tjäna pengar genom abonnemang, engångsbetalningar eller provision.
Börja med en enkel MVP och testa om folk vill betala.
""".strip()
