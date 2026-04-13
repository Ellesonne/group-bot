import os
import logging
import random
from datetime import datetime
from telegram.ext import ApplicationBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN_GROUP", "")
GROUP_ID = int(os.environ.get("GROUP_ID", "-1003554027522"))

# ═══════════════════════════════════════════════════════════════
# FUNNEL - JAVE (E Hene → E Premte)
# 10h UTC = 12h Kosovo → PROVE SOCIALE (pauze dreke)
# 16h UTC = 18h Kosovo → DHIMBJE + HUMBJE (dalja nga puna)
# 19h30 UTC = 21h30 Kosovo → URGENCE (para gjumit)
#
# FUNNEL - FUNDJAVË (E Shtune + E Diele)
# 10h UTC = 12h Kosovo → KURSE + FORMIM
# 16h UTC = 18h Kosovo → LIVE + KOMUNITET
# 19h30 UTC = 21h30 Kosovo → GATIHU PER JAVEN E ARDHSHME
# ═══════════════════════════════════════════════════════════════

# ─── MESAZHET E JAVES ──────────────────────────────────────────

JAVE_MENGJES = [  # 12h Kosovo - Prove sociale
    "Nje mesazh nga nje anetare e grupit VIP:\n\n'Sinjali i sotem: +340€ ne 2 ore. Thjesht kopjova entryn dhe prova TP.'\n\nKjo eshte rutina e perditshme.\nTi ende jashte?\n\nDergo « GO » te @ElsonDigital 👇",

    "Ndersa ti po ha drekën — anetaret e grupit VIP po tregtojne.\n\nMinir Halimi: +467€ ne nje dite.\nAlteron Loshaj: +2,584€ profit total.\nMaroine El Abdi: +10,468€ aktive tani.\n\nKeta filluan sic je ti — pa eksperience, pa njohuri.\nVeprojne. Fitojne.\n\nDergo « GO » te @ElsonDigital 👇",

    "Sot ne mengjes grupi VIP ka marre nje sinjal.\n\nAnetaret qe ishin brenda — fituan.\nAnetaret qe nuk ishin — po shikojne.\n\nCilit grup i perkes ti?\n\nDergo « GO » te @ElsonDigital 👇",

    "Pauza e drekës eshte momenti i duhur per te marre nje vendim. ⏰\n\nNje vendim i vogel sot:\n300€ ne llogarise tuaj te brokerit.\nSinjale te gatshme cdo dite.\nElson dhe ekipi i tij prane teje.\n\nDergo « GO » te @ElsonDigital 👇",

    "Fisnik Krasniqi ishte aty ku je ti — zero njohuri, zero eksperience.\nBeri +66€ ne trades e para duke ndjekur sinjalet.\n\nNuk duhet te dish trading.\nDuhet vetem te jesh brenda.\n\nDergo « GO » te @ElsonDigital 👇",
]

JAVE_DITE = [  # 18h Kosovo - Dhimbje + humbje
    "Llogarite bashke:\n\nNese nje anetare VIP fiton mesatarisht 50€ ne dite — kjo eshte:\n📅 50€ sot\n📅 350€ kete jave\n📅 1,500€ kete muaj\n\nTi sot ke fituar 0€.\nNeser mund te fillosh.\n\nDergo « GO » te @ElsonDigital 👇",

    "Sapo dole nga puna. 🕕\n\nNderkohe grupi VIP beri 2 sinjale sot.\nAnetaret fituan ndersa ti ishe ne pune.\n\nIdeja eshte te kesh dy burime te ardhurash:\n✅ Puna jote\n✅ Trading me sinjalet tona\n\nDergo « GO » te @ElsonDigital 👇",

    "3 muaj me pare nje person vendosi te hyjne ne grupin VIP.\nSot nxori 700€ cash dhe ka ende 2,584€ profit aktiv.\n\n3 muaj me pare ti kishe po ate mundesie.\nNuk veprove.\n\nSot ke perseri ate mundesie.\nCfar do te besh kete here?\n\nDergo « GO » te @ElsonDigital 👇",

    "Challenge i grupit VIP: 300€ → 3,000€ brenda 30 diteve. 🎯\n\nEkipi Besa Digital ndihmon 5 persona per ta arritur kete.\nSinjale. Live. Mentorship personal.\n\nKa vetem 5 vende.\nDergo « GO » te @ElsonDigital tani 👇",

    "Njerezit qe vepruan 3 muaj me pare — sot po nxjerrin para. 💸\nNjerezit qe po presin sot — do te thone 'duhej ta beja me heret'.\n\nTi ne cilin grup do te jesh pas 3 muajsh?\n\nDergo « GO » te @ElsonDigital 👇",
]

JAVE_MBREMJE = [  # 21h30 Kosovo - Urgence para gjumit
    "Para se te flesh sonte — nje pyetje:\n\nNese 6 muaj me pare kishe filluar — ku do te ishe tani?\n\nMos lejo qe pas 6 muajsh te besh perseri kete pyetje.\nVepro sonte.\n\nDergo « GO » te @ElsonDigital 👇",

    "Sonte eshte momenti. 🔥\n\nJo neser. Jo te henen. Jo 'kur te kem kohe'.\n\nAlteron nuk priti momentin perfekt.\nMinir nuk priti.\nFisnik nuk priti.\n\nEdhe ti nuk duhet te presesh.\n\nDergo « GO » te @ElsonDigital tani 👇",

    "Mbremja e sodit eshte momenti i fundit per te hyre me konditat aktuale. ⏳\n\nNeser nuk premtoj qe vendi eshte ende i lire.\n\n✅ Shoqerim dhe formim nga A deri Z\n✅ Asnje njohuri e nevojshme\n✅ 300€ per me fillua\n\nDergo « GO » tani te @ElsonDigital 🔥",

    "Nese nuk je i motivuar — del pi kanalit. 🚪\n\nPo kerkoj vetem njerez te gateshme me vepruar.\nAta qe hezitojne kane vendin e tyre diku tjeter.\nAmbiziozet — kane vendin e tyre ketu.\n\nJe ambicioz? Dergo « GO » te @ElsonDigital 💪🏻",

    "Para se te flesh sonte:\n\n300€ ne llogarise tuaj te brokerit.\nSinjale te gatshme cdo dite.\nElson dhe ekipi tij prane teje.\n\nNesermenden zgjohet nje person ndryshe. 🌙\n\nDergo « GO » te @ElsonDigital 👇",
]

# ─── MESAZHET E FUNDJAVËS ──────────────────────────────────────

FUNDJAVË_MENGJES = [  # 12h Kosovo - Kurse + formim
    "Tregu eshte mbyllur kete fundjavë. 📚\n\nPor ky eshte momenti me i mire per me u gatu.\n\nNe grupin VIP kete fundjavë:\n✅ Kurse trading te plota\n✅ Materiale ekskluzive\n✅ Strategji per javen e ardhshme\n\nAnetaret qe mesojne fundjavën — fitojne javen tjeter.\n\nDergo « GO » te @ElsonDigital 👇",

    "E diela eshte dita me e mire per me fillua. ☀️\n\nPse?\n\nSe ka kohe. Se tregu hapet te henen.\nSe mund te mesosh gjithcka sot dhe te jesh gati neser.\n\nGrupi VIP te jep kurse, materiale dhe strategji — te gjitha kete fundjavë.\n\nDergo « GO » te @ElsonDigital 👇",

    "Ndersa nje person pushon kete fundjavë — nje tjeter po pergatitet. 📖\n\nGrupi VIP i Elsonit ka materiale formimi qe anetaret i studjojne fundjavën:\n✅ Si te lexosh grafiqet\n✅ Si te menaxhosh rrezikun\n✅ Strategjite me te mira per Gold dhe Forex\n\nE hena fillon. A je gati?\n\nDergo « GO » te @ElsonDigital 👇",

    "Fundjavë pa trading = fundjavë per te mesuar. 🧠\n\nKurset e grupit VIP jane te dizajnuara per fillestar total.\nZero njohuri? Zero problem.\nBrenda nje fundjavë di me shume se shumica.\n\nDergo « GO » te @ElsonDigital 👇",

    "Nje fundjavë e investuar ne formim = javë me fitim. 💡\n\nAlteron Loshaj studjoi nje fundjavë.\nJaven tjeter beri fitimin e pare.\nTani ka +2,584€ profit total.\n\nTi kur fillon?\n\nDergo « GO » te @ElsonDigital 👇",
]

FUNDJAVË_DITE = [  # 18h Kosovo - Live + komunitet
    "🔴 LIVE KETE JAVE me Elson Bytyqi.\n\nElson tregton LIVE — sheh cdo vendim, cdo analize, cdo trade ne kohe reale.\n\nPyetje? I pergjigjemi live.\nStrategji? I shpjegojme live.\n\nKjo eshte eksperienca qe nuk gjen askund tjeter.\n\nDergo « GO » te @ElsonDigital per te hyre para livit 👇",

    "Anetaret e grupit VIP nuk jane vetem — jane nje komunitet. 🤝\n\n10,000+ njerez qe:\n✅ Ndajne trades\n✅ Ndihmojne njeri-tjetrin\n✅ Mesojne bashke\n✅ Fitojne bashke\n\nTi fundjavën e kalon vetem.\nAta e kalojne bashke duke u pergatitur per javen e ardhshme.\n\nDergo « GO » te @ElsonDigital 👇",

    "Cfare bejne anetaret e grupit VIP kete fundjavë:\n\n📚 Studiojne materialet e kursit\n🎯 Analizojne javen e shkuar\n📊 Pergatisin strategjine per te henen\n🔴 Ndjekin livin e Elsonit\n\nTi cfar bën?\n\nDergo « GO » te @ElsonDigital 👇",

    "Live i javes me Elson. 🎥\n\nNje here ne jave, Elson hap llogarise e tij dhe tregton live perpara te gjithave.\nSheh si mendon nje tregtues profesionist.\nSheh si merr vendime ne kohe reale.\nBen pyetje — merr pergjigje direkte.\n\nKjo eksperience eshte vetem per anetaret VIP.\n\nDergo « GO » te @ElsonDigital 👇",

    "Projektet ekskluzive te grupit VIP — vetem per anetaret. 🔐\n\nPerveç tradingut, anetaret VIP kane akses ne mundesi te tjera:\n✅ Projekte investimi ekskluzive\n✅ Te ardhura shtese jashte tradingut\n✅ Informacion qe nuk del jashte grupit\n\nKeto nuk publikohen kurre jashte.\n\nDergo « GO » te @ElsonDigital 👇",
]

FUNDJAVË_MBREMJE = [  # 21h30 Kosovo - Gatihu per javen
    "E hena fillon pas 36 oreve. ⏰\n\nAnetaret e grupit VIP jane gati.\nKane studjuar. Kane analizuar. Kane nje plan.\n\nTi — a je gati per javen e ardhshme?\n\nNese nuk je brenda akoma — tani eshte momenti.\nDergo « GO » te @ElsonDigital 👇",

    "Nje fundjavë e perdorur mire ndryshon javen tjeter. 💪🏻\n\nAnetaret VIP kete fundjavë:\n✅ Ndoqen kurset e tradingut\n✅ Ndoqen livin e Elsonit\n✅ U pergatiten per sinjalet e javes\n\nTi mund te fillosh kete fundjavë.\nDergo « GO » te @ElsonDigital 👇",

    "Imagjino: E hena fillon dhe ti ke:\n✅ Sinjale te gatshme\n✅ Nje strategji te qarte\n✅ Elson dhe ekipin prane\n✅ Nje komunitet qe te ndihmon\n\nKjo eshte realiteti i anetareve VIP cdo te hene.\n\nDo te ndryshosh kete fundjavë?\nDergo « GO » te @ElsonDigital 👇",

    "Para se te flesh sonte — nje mendim:\n\nNeser fillon jave tjeter.\nCdo jave qe kalon jashte grupit eshte nje jave fitim i humbur.\n\nNje vendim i vogel sonte ndryshon gjithcka.\n\nDergo « GO » te @ElsonDigital 🌙👇",

    "Sonte mbyllet fundjavë. ⏳\n\nE hena sjell sinjale te reja, mundesi te reja, fitim te ri.\n\nAnetaret VIP jane gati.\nTi — a do te jesh brenda te henen?\n\nTani ose kurre.\nDergo « GO » te @ElsonDigital 🔥",
]

# ─── LOGIC ────────────────────────────────────────────────────
sent = {"mengjes": [], "dite": [], "mbremje": []}

def get_msg(slot, is_weekend):
    global sent
    if is_weekend:
        pools = {"mengjes": FUNDJAVË_MENGJES, "dite": FUNDJAVË_DITE, "mbremje": FUNDJAVË_MBREMJE}
    else:
        pools = {"mengjes": JAVE_MENGJES, "dite": JAVE_DITE, "mbremje": JAVE_MBREMJE}

    pool = pools[slot]
    available = [m for m in pool if m not in sent[slot]]
    if not available:
        sent[slot] = []
        available = pool
    msg = random.choice(available)
    sent[slot].append(msg)
    return msg

async def send_mengjes(application):
    now = datetime.utcnow()
    is_weekend = now.weekday() >= 5
    msg = get_msg("mengjes", is_weekend)
    await application.bot.send_message(chat_id=GROUP_ID, text=msg)
    logging.info(f"Mesazh mengjes {'fundjavë' if is_weekend else 'jave'} derguar")

async def send_dite(application):
    now = datetime.utcnow()
    is_weekend = now.weekday() >= 5
    msg = get_msg("dite", is_weekend)
    await application.bot.send_message(chat_id=GROUP_ID, text=msg)
    logging.info(f"Mesazh dite {'fundjavë' if is_weekend else 'jave'} derguar")

async def send_mbremje(application):
    now = datetime.utcnow()
    is_weekend = now.weekday() >= 5
    msg = get_msg("mbremje", is_weekend)
    await application.bot.send_message(chat_id=GROUP_ID, text=msg)
    logging.info(f"Mesazh mbremje {'fundjavë' if is_weekend else 'jave'} derguar")

def main():
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    scheduler = AsyncIOScheduler()
    # 10h UTC = 12h Kosovo
    scheduler.add_job(send_mengjes, "cron", hour=10, minute=0, args=[app])
    # 16h UTC = 18h Kosovo
    scheduler.add_job(send_dite, "cron", hour=16, minute=0, args=[app])
    # 19h30 UTC = 21h30 Kosovo
    scheduler.add_job(send_mbremje, "cron", hour=19, minute=30, args=[app])

    scheduler.start()
    print("Bot group aktiv — 12h/18h/21h30 Kosovo | Jave + Fundjavë")
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
