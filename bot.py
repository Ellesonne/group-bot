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
# FUNNEL PSIKOLOGJIK - 3 mesazhe ne dite
#
# 10h Kosovo → KURRESHTJE + PROVE SOCIALE
#              "Te tjeret po fitojne — ti nuk je ende brenda"
#
# 15h Kosovo → DHIMBJE + HUMBJE E LLOGARITUR
#              "Sa ke humbur sot duke pritur"
#
# 20h Kosovo → URGENCE + SKARSITE
#              "Mbyllet sonte — neser nuk eshte me"
# ═══════════════════════════════════════════════════════════════

MESAZHET_MENGJES = [  # 8h UTC = 10h Kosovo
    "Nje mesazh nga nje anetare e grupit VIP sot ne mengjes:\n\n'Sinjali i sotem: +340$ ne 2 ore. Thjesht kopjova entryn dhe prova TP.'\n\nKjo eshte rutina e perditshme per anetaret tane.\nTi ende jashte?\n\nDergo « GO » te @ElsonDigital 👇",

    "Ndersa ti po lexon kete — Minir Halimi beri +467$ ne nje dite. Alteron Loshaj nxori 700€ cash. Maroine El Abdi ka 10,468€ aktive.\n\nKeta nuk jane njerez te vecante.\nKeta jane njerez qe vepruan kur kishin mundesine.\n\nTi e ke mundesine tani.\nDergo « GO » te @ElsonDigital 👇",

    "Sot ne mengjes grupi VIP ka marre nje sinjal.\n\nAnetaret qe ishin brenda — po fitojne tani.\nAnetaret qe nuk ishin — po shikojne.\n\nCilit grup i perkes ti?\n\nDergo « GO » te @ElsonDigital 👇",

    "Fisnik Krasniqi ishte aty ku je ti — zero njohuri, zero eksperience.\nBeri +66€ ne trades e para duke ndjekur sinjalet.\n\nNuk duhet te dish trading per me fituar.\nDuhet vetem te jesh brenda.\n\nDergo « GO » te @ElsonDigital 👇",

    "Grupi VIP i Elsonit ka tani mbi 10,000 anetare aktiv. 📈\n\nCdo dite sinjale.\nCdo jave live.\nCdo muaj anetare te ri qe fitojne per here te pare.\n\nVendi eshte i lire ende — por jo per gjate.\nDergo « GO » te @ElsonDigital 👇",
]

MESAZHET_DITE = [  # 13h UTC = 15h Kosovo
    "Llogarite bashke:\n\nNese nje anetare VIP fiton mesatarisht 50€ ne dite — kjo eshte:\n📅 50€ sot\n📅 350€ kete jave\n📅 1,500€ kete muaj\n\nTi sot ke fituar 0€.\nNeser mund te fillosh.\n\nDergo « GO » te @ElsonDigital 👇",

    "3 muaj me pare nje person vendosi te hyjne ne grupin VIP.\nSot nxori 700€ cash dhe ka ende 2,584€ profit aktiv.\n\n3 muaj me pare ti kishe po ate mundesie.\nNuk veprove.\n\nSot ke perseri ate mundesie.\nCfar do te besh kete here?\n\nDergo « GO » te @ElsonDigital 👇",

    "Challenge i grupit VIP: 300€ → 3,000€ brenda 30 diteve. 🎯\n\nEkipi Besa Digital ndihmon 5 persona per ta arritur kete.\nSinjale. Live. Mentorship personal.\n\nKa vetem 5 vende.\nDergo « GO » te @ElsonDigital tani 👇",

    "Cfare merr kur hyn ne grupin VIP:\n\n✅ Sinjale ditore Forex/Gold/Crypto\n✅ Live 1 here ne jave me Elson\n✅ Kurse trading nga zero\n✅ Sesione 1-on-1 me tregtues pro\n✅ Projekte fitimprures ekskluzive\n✅ Komunitet 10,000+ anetare\n\nGjithcka kjo fillon me 300€ depozite — qe i mban TI ne llogarise tuaj.\n\nDergo « GO » te @ElsonDigital 👇",

    "Njerezit qe vepruan sot 3 muaj me pare — po nxjerrin para tani. 💸\nNjerezit qe po presin sot — do te thone 'duhej ta beja me heret'.\n\nTi ne cilin grup do te jesh pas 3 muajsh?\n\nVepro tani. Dergo « GO » te @ElsonDigital 👇",
]

MESAZHET_MBREMJE = [  # 18h UTC = 20h Kosovo
    "Mbremja e sodit eshte momenti i fundit per te hyre ne grupin VIP me konditat aktuale. ⏳\n\nNeser nuk premtoj qe vendi eshte ende i lire.\n\nNese edhe ti don akses brenda disa minutave:\n\n✅ Shoqerim dhe formim nga A deri Z\n✅ Asnje njohuri e nevojshme\n✅ 300€ dhe 3,000€ ne jave\n\nDergo « GO » tani te @ElsonDigital 🔥",

    "Pyetje per ty para se te flesh sonte:\n\nNese 6 muaj me pare kishe filluar — ku do te ishe tani?\n\nMos lejo qe pas 6 muajsh te besh perseri kete pyetje.\nVepro sonte.\n\nDergo « GO » te @ElsonDigital 👇",

    "Nese nuk je i motivuar — del pi kanalit. 🚪\n\nPo kerkoj vetem njerez te gateshme me vepruar.\nAta qe hezitojne kane vendin e tyre diku tjeter.\nAmbiziozet — kane vendin e tyre ketu.\n\nJe ambicioz? Dergo « GO » te @ElsonDigital 💪🏻",

    "Sonte eshte momenti. 🔥\n\nJo neser. Jo te henen. Jo 'kur te kem kohe'.\n\nAlteron Loshaj nuk priti momentin perfekt.\nMinir Halimi nuk priti.\nFisnik Krasniqi nuk priti.\n\nEdhe ti nuk duhet te presesh.\n\nDergo « GO » te @ElsonDigital tani 👇",

    "Para se te flesh sonte — nje vendim i vogel:\n\n300€ ne llogarise tuaj te brokerit.\nSinjale te gatshme cdo dite.\nElson dhe ekipi tij prane teje.\n\nNesermenden zgjohet nje person ndryshe.\n\nDergo « GO » te @ElsonDigital 🌙",
]

sent_mengjes = []
sent_dite = []
sent_mbremje = []

async def send_mengjes(application):
    global sent_mengjes
    available = [m for m in MESAZHET_MENGJES if m not in sent_mengjes]
    if not available:
        sent_mengjes = []
        available = MESAZHET_MENGJES
    msg = random.choice(available)
    sent_mengjes.append(msg)
    await application.bot.send_message(chat_id=GROUP_ID, text=msg)
    logging.info("Mesazh mengjes derguar")

async def send_dite(application):
    global sent_dite
    available = [m for m in MESAZHET_DITE if m not in sent_dite]
    if not available:
        sent_dite = []
        available = MESAZHET_DITE
    msg = random.choice(available)
    sent_dite.append(msg)
    await application.bot.send_message(chat_id=GROUP_ID, text=msg)
    logging.info("Mesazh dite derguar")

async def send_mbremje(application):
    global sent_mbremje
    available = [m for m in MESAZHET_MBREMJE if m not in sent_mbremje]
    if not available:
        sent_mbremje = []
        available = MESAZHET_MBREMJE
    msg = random.choice(available)
    sent_mbremje.append(msg)
    await application.bot.send_message(chat_id=GROUP_ID, text=msg)
    logging.info("Mesazh mbremje derguar")

def main():
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    scheduler = AsyncIOScheduler()
    # 8h UTC = 10h Kosovo
    scheduler.add_job(send_mengjes, "cron", hour=8, minute=0, args=[app])
    # 13h UTC = 15h Kosovo
    scheduler.add_job(send_dite, "cron", hour=13, minute=0, args=[app])
    # 18h UTC = 20h Kosovo
    scheduler.add_job(send_mbremje, "cron", hour=18, minute=0, args=[app])

    scheduler.start()
    print("Bot group aktiv — Funnel 3 faza: Prove → Dhimbje → Urgence")
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
