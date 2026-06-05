def create_pitch_for_lead(lead):
    company = lead.company_name or "ert företag"
    industry = lead.industry or "tjänsteföretag"
    city = lead.city or "Sverige"

    subject = f"Fler kundförfrågningar till {company}"

    body = f"""Hej {company},

Jag såg att ni arbetar inom {industry} i {city} och ville höra om ni just nu tar emot fler uppdrag.

Jag bygger FlerKunder, ett system som hjälper lokala tjänsteföretag att hitta relevanta företag/kunder, skapa personliga kontaktutskick och få fler bokade samtal utan att lägga timmar på manuell prospektering.

För ett företag som {company} kan det handla om att:
- hitta fler potentiella kunder i rätt område
- följa upp snabbare
- få bättre struktur på leads
- skapa fler bokade samtal varje vecka

Jag kan visa ett kort exempel på hur ett sådant flöde skulle kunna se ut för er.

Är ni öppna för ett kort samtal på 10 minuter nästa vecka?

Med vänliga hälsningar
Elias
FlerKunder
"""

    return subject, body