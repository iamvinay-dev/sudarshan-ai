# -*- coding: utf-8 -*-
"""
knowledge_base.py
------------------
This file is the ENTIRE "database" of Sudarshan AI.
There is NO external database. All pilgrim information lives right here
as plain Python dictionaries, so the bot works with zero setup cost.

Structure:
    KNOWLEDGE_BASE = {
        "category_key": {
            "title": "Human readable title with emoji",
            "qas": [ {"q": "...", "a": "..."}, ... ]
        },
        ...
    }

To add more knowledge later:
    1. Pick the right category below (or add a new one).
    2. Add a new {"q": "...", "a": "..."} entry to its "qas" list.
    That's it — the AI automatically uses it on the next restart.
"""

KNOWLEDGE_BASE = {

    "darshan": {
        "title": "🎟️ Darshan & Tickets",
        "summary": (
            "*🎟️ Darshan & Tickets*\n\n"
            "• *Sarva Darshan* – Free, no ticket needed\n"
            "• *Special Entry Darshan* – ₹300 (advance booking)\n"
            "• *Divya Darshan* – Via Alipiri / Srivari Mettu footpaths\n"
            "• *Senior Citizen / Differently Abled* – Special quota available\n"
            "• Carry your *ticket + original photo ID* for entry\n"
        ),
        "summary_te": (
            "*🎟️ దర్శనం & టికెట్లు*\n\n"
            "• *సర్వ దర్శనం* – ఉచితం, టికెట్ అవసరం లేదు\n"
            "• *స్పెషల్ ఎంట్రీ దర్శనం* – ₹300 (ముందస్తు బుకింగ్)\n"
            "• *దివ్య దర్శనం* – అలిపిరి / శ్రీవారి మెట్టు మార్గాల ద్వారా\n"
            "• *సీనియర్ సిటిజన్ / దివ్యాంగుల* – ప్రత్యేక కోటా అందుబాటులో\n"
            "• ప్రవేశానికి *టికెట్ + ఒరిజినల్ ఫోటో ID* తీసుకురావాలి\n"
        ),
        "qas": [
            {"q": "What is Tirumala Temple?",
             "a": "Tirumala Temple, also known as Sri Venkateswara Swamy Temple, is one of the most sacred Hindu temples dedicated to Lord Venkateswara, an incarnation of Lord Vishnu. It is located in Tirumala, Andhra Pradesh."},
            {"q": "Where is Tirumala Temple located?",
             "a": "Tirumala Temple is located on the Seven Hills (Seshachalam Hills) in Tirumala, near Tirupati, Andhra Pradesh, India."},
            {"q": "What are the different types of darshan?",
             "a": "The major darshan categories are: Sarva Darshan (Free), Special Entry Darshan (₹300), Divya Darshan, Senior Citizen Darshan, Differently Abled Darshan, Infant Entry, and Seva Darshan."},
            {"q": "What is Sarva Darshan?",
             "a": "Sarva Darshan is the free darshan available to all devotees without any ticket fee. Waiting time depends on the crowd."},
            {"q": "What is Special Entry Darshan?",
             "a": "Special Entry Darshan is a paid darshan that costs ₹300 per person and is available through advance booking subject to slot availability."},
            {"q": "What is Divya Darshan?",
             "a": "Divya Darshan is provided to eligible pilgrims who reach Tirumala through the Alipiri or Srivari Mettu footpaths, subject to TTD guidelines."},
            {"q": "Who can use Senior Citizen Darshan?",
             "a": "Eligible senior citizens can avail this darshan as per the latest TTD eligibility rules. A valid government-issued photo ID is required."},
            {"q": "Is there a special darshan for differently abled devotees?",
             "a": "Yes. TTD provides special darshan arrangements for differently abled devotees according to current guidelines."},
            {"q": "How do I book a darshan ticket?",
             "a": "Darshan tickets can be booked through TTD's official booking channels (https://tirumala.org) whenever booking slots are released."},
            {"q": "When are SSD tokens released?",
             "a": "SSD token release dates change regularly. Please check the latest official TTD announcement or ask again closer to your travel date."},
            {"q": "When are ₹300 tickets released?",
             "a": "The release schedule changes periodically. Refer to the latest TTD announcement for the current booking date and time."},
            {"q": "Can I book tickets offline?",
             "a": "Certain services may be available through designated TTD booking counters, subject to availability and current policy."},
            {"q": "What ID proof is required?",
             "a": "Carry the original government-issued photo ID used during booking."},
            {"q": "Is Aadhaar compulsory?",
             "a": "Aadhaar is not always mandatory. Other valid government-issued photo IDs are accepted according to TTD guidelines."},
            {"q": "What is the QR code on my ticket used for?",
             "a": "The QR code is scanned during entry to verify your booking details."},
            {"q": "How early should I reach?",
             "a": "Arrive at least 1 hour before the reporting time mentioned on your ticket unless instructed otherwise by TTD."},
            {"q": "What happens if I miss my reporting time?",
             "a": "Entry after the reporting time depends on TTD's operational policy. Always arrive before your scheduled time."},
            {"q": "Can I cancel my ticket?",
             "a": "Cancellation and refund depend on the ticket type and TTD's current cancellation policy."},
            {"q": "Can I change my booking date?",
             "a": "Date modification is generally not available unless permitted under TTD's current policy."},
            {"q": "How can I download my ticket?",
             "a": "You can download your booking confirmation through the official TTD booking platform, https://tirumala.org."},
            {"q": "Do children require a ticket?",
             "a": "Ticket requirements depend on the child's age and the prevailing TTD guidelines."},
            {"q": "How long is the waiting time?",
             "a": "Waiting time varies based on crowd levels, festivals, weekends, and the darshan category."},
            {"q": "Can I check the live crowd?",
             "a": "For the latest live crowd and queue information, please refer to official TTD updates."},
            {"q": "Is VIP Darshan available?",
             "a": "VIP Darshan is governed by TTD's official eligibility criteria and is not generally available for public booking."},
            {"q": "What should I carry for darshan?",
             "a": "Carry your ticket (if applicable), the original government-issued photo ID used during booking, essential medicines if required, and avoid carrying unnecessary luggage."},
        ],
    },

    "accommodation": {
        "title": "🏨 Accommodation & Free Stay",
        "summary": (
            "*🏨 Accommodation & Free Stay*\n\n"
            "• *Vishnu Nivasam* – Opposite Tirupati Railway Station; rooms, free halls, lockers\n"
            "• *Madhava Nilayam* – Opposite Tirumala bus stand; free rest halls, lockers, Anna Prasadam\n"
            "• Free *lockers & bathing* facilities at both complexes\n"
            "• Choose based on location: Tirupati → Vishnu Nivasam, Tirumala → Madhava Nilayam\n"
        ),
        "summary_te": (
            "*🏨 వసతి & ఉచిత బస*\n\n"
            "• *విష్ణు నివాసం* – తిరుపతి రైల్వే స్టేషన్ ఎదురుగా; గదులు, ఉచిత హాళ్లు, లాకర్లు\n"
            "• *మాధవ నిలయం* – తిరుమల బస్ స్టాండ్ ఎదురుగా; ఉచిత రెస్ట్ హాళ్లు, లాకర్లు, అన్న ప్రసాదం\n"
            "• రెండు చోట్లా ఉచిత *లాకర్లు & స్నానాల* సదుపాయం\n"
            "• తిరుపతిలో ఉంటే → విష్ణు నివాసం, తిరుమలలో ఉంటే → మాధవ నిలయం\n"
        ),
        "qas": [
            {"q": "Does TTD provide free accommodation?",
             "a": "Yes. TTD provides free resting halls, dormitories, and accommodation facilities for pilgrims at both Tirupati and Tirumala, subject to availability."},
            {"q": "What is Vishnu Nivasam?",
             "a": "Vishnu Nivasam is a major TTD accommodation complex located directly opposite Tirupati Railway Station. It provides paid rooms, free waiting halls, lockers, bathing facilities, and other amenities for pilgrims."},
            {"q": "Where is Vishnu Nivasam located?",
             "a": "Vishnu Nivasam is situated opposite Tirupati Railway Station, making it convenient for devotees arriving by train. It is also a short distance from the Tirupati bus stand."},
            {"q": "Can I stay at Vishnu Nivasam before my darshan?",
             "a": "Yes. Pilgrims can use the accommodation and waiting facilities at Vishnu Nivasam, subject to availability and TTD rules."},
            {"q": "Does Vishnu Nivasam have free waiting halls?",
             "a": "Yes. Vishnu Nivasam provides free waiting and resting facilities for pilgrims in addition to paid rooms."},
            {"q": "Are lockers available at Vishnu Nivasam?",
             "a": "Yes. Free locker facilities are available for pilgrims to safely store their luggage while visiting the temple."},
            {"q": "Are bathing facilities available at Vishnu Nivasam?",
             "a": "Yes. Pilgrims can use bathing and toilet facilities available within the complex."},
            {"q": "Can I get a room at Vishnu Nivasam without advance booking?",
             "a": "Depending on availability, certain rooms are allotted through current (offline) booking. Advance booking availability depends on the room category and TTD policy."},
            {"q": "What is Madhava Nilayam?",
             "a": "Madhava Nilayam is a Pilgrim Amenities Complex (PAC-2) in Tirumala that offers large resting halls, free lockers, Anna Prasadam, tonsure facilities, first-aid services, and resting areas for devotees."},
            {"q": "Where is Madhava Nilayam located?",
             "a": "Madhava Nilayam is located opposite the Tirumala Balaji Bus Stand, making it easy for pilgrims arriving by bus."},
            {"q": "Can pilgrims rest at Madhava Nilayam?",
             "a": "Yes. Pilgrims can use the free resting halls available at Madhava Nilayam, subject to availability."},
            {"q": "Are lockers available at Madhava Nilayam?",
             "a": "Yes. Thousands of free lockers are available for pilgrims to safely store their belongings."},
            {"q": "Is free Anna Prasadam available at Madhava Nilayam?",
             "a": "Yes. Free Anna Prasadam is provided for pilgrims at Madhava Nilayam."},
            {"q": "Is tonsure (hair offering) available at Madhava Nilayam?",
             "a": "Yes. Tonsure facilities are available for pilgrims at Madhava Nilayam."},
            {"q": "Is first aid available at Madhava Nilayam?",
             "a": "Yes. A first-aid center is available to assist pilgrims in case of minor medical needs."},
            {"q": "Which accommodation is best for pilgrims arriving by train?",
             "a": "Vishnu Nivasam is one of the most convenient choices because it is located directly opposite Tirupati Railway Station."},
            {"q": "Which accommodation is best for pilgrims already in Tirumala?",
             "a": "Pilgrims can use TTD accommodation complexes or Pilgrim Amenities Complexes such as Madhava Nilayam for resting and other facilities."},
            {"q": "Can I keep my luggage safely before darshan?",
             "a": "Yes. TTD provides locker facilities at several accommodation complexes and pilgrim amenities centers, including Vishnu Nivasam and Madhava Nilayam."},
            {"q": "Can I take a bath before darshan?",
             "a": "Yes. Bathing facilities are available at various TTD accommodation complexes and pilgrim amenities centers for devotees."},
            {"q": "Which free accommodation should I choose?",
             "a": "If you are in Tirupati, Vishnu Nivasam is a convenient option near the railway station. If you are already in Tirumala, Madhava Nilayam is a good choice for resting, lockers, Anna Prasadam, and other pilgrim facilities."},
        ],
    },

    "transport": {
        "title": "🚌 Transportation",
        "summary": (
            "*🚌 Transportation*\n\n"
            "• *Bus* – APSRTC buses run Tirupati ↔ Tirumala frequently\n"
            "• *Free buses* – Railway Station → Alipiri / Srivari Mettu\n"
            "• *Own vehicle* – Allowed via Alipiri Check Post\n"
            "• *Walking* – Srivari Mettu (2.4 km) or Alipiri (11 km)\n"
            "• *Inside Tirumala* – Free 'Dharma Ratham' buses connect key spots\n"
        ),
        "summary_te": (
            "*🚌 రవాణా*\n\n"
            "• *బస్సు* – APSRTC బస్సులు తిరుపతి ↔ తిరుమల మధ్య తరచుగా నడుస్తాయి\n"
            "• *ఉచిత బస్సులు* – రైల్వే స్టేషన్ → అలిపిరి / శ్రీవారి మెట్టు\n"
            "• *సొంత వాహనం* – అలిపిరి చెక్ పోస్ట్ ద్వారా అనుమతి\n"
            "• *నడక* – శ్రీవారి మెట్టు (2.4 కి.మీ) లేదా అలిపిరి (11 కి.మీ)\n"
            "• *తిరుమలలో* – ఉచిత 'ధర్మ రథం' బస్సులు ముఖ్య ప్రదేశాలను కలుపుతాయి\n"
        ),
        "qas": [
            {"q": "How can I travel from Tirupati to Tirumala?",
             "a": "You can travel by APSRTC bus, private taxi, your own vehicle, or by walking through the Alipiri or Srivari Mettu footpaths."},
            {"q": "Are APSRTC buses available from Tirupati to Tirumala?",
             "a": "Yes. APSRTC operates frequent buses between Tirupati and Tirumala throughout the day."},
            {"q": "Where can I board APSRTC buses in Tirupati?",
             "a": "You can board buses from the Tirupati Central Bus Station and other designated APSRTC boarding points."},
            {"q": "Are buses available from Tirupati Railway Station to Tirumala?",
             "a": "Yes. APSRTC buses are available for pilgrims arriving at Tirupati Railway Station."},
            {"q": "Is there a free bus from Tirupati Railway Station to Alipiri?",
             "a": "Yes. APSRTC operates free buses from Tirupati Railway Station to the Alipiri footpath entrance at regular intervals."},
            {"q": "Is there a free bus from Tirupati Railway Station to Srivari Mettu?",
             "a": "Yes. APSRTC operates free buses for pilgrims travelling to the Srivari Mettu footpath."},
            {"q": "Can I travel to Tirumala in my own vehicle?",
             "a": "Yes. Private cars, bikes, and other vehicles are permitted to travel to Tirumala after completing security checks at Alipiri Check Post."},
            {"q": "Is there any toll for vehicles entering Tirumala?",
             "a": "Vehicles pass through the Alipiri Check Post where security verification is carried out. Entry procedures may change according to TTD regulations."},
            {"q": "Can I hire a taxi to Tirumala?",
             "a": "Yes. Taxis and cab services are available from Tirupati Railway Station, Airport, and Bus Station."},
            {"q": "Are auto-rickshaws available?",
             "a": "Yes. Auto-rickshaws are available throughout Tirupati for local transportation."},
            {"q": "How far is Tirupati Railway Station from Alipiri?",
             "a": "Alipiri is approximately 4 km from Tirupati Railway Station."},
            {"q": "How far is Tirupati Airport from Tirumala?",
             "a": "Tirupati Airport is approximately 40 km from Tirumala."},
            {"q": "How can I travel from Tirupati Airport to Tirumala?",
             "a": "You can use APSRTC buses, prepaid taxis, app-based cabs, or private vehicles."},
            {"q": "Which is the shortest walking route to Tirumala?",
             "a": "Srivari Mettu is the shorter footpath, covering about 2.4 km with around 2,400 steps."},
            {"q": "Which is the longest walking route?",
             "a": "Alipiri Mettu is about 11 km long and is the traditional walking route with approximately 3,500+ steps."},
            {"q": "Which footpath is open 24 hours?",
             "a": "Alipiri Footpath generally operates throughout the day according to TTD guidelines."},
            {"q": "What facilities are available on the Alipiri Footpath?",
             "a": "Drinking water, toilets, shelters, luggage transport, security, medical assistance, canteens, and biometric counters are available."},
            {"q": "What facilities are available on the Srivari Mettu Footpath?",
             "a": "Drinking water, security, biometric counters, luggage transport, medical assistance, and resting facilities are available."},
            {"q": "Is luggage transport available for footpath pilgrims?",
             "a": "Yes. TTD provides free luggage transportation from Tirupati to Tirumala for pilgrims walking through the designated footpaths."},
            {"q": "Where can I collect my luggage in Tirumala?",
             "a": "Luggage can be collected from the designated TTD luggage delivery counters after presenting the token issued at the time of deposit."},
            {"q": "Is medical assistance available on the footpath?",
             "a": "Yes. TTD provides 24-hour medical assistance along both walking routes."},
            {"q": "Is drinking water available on the footpath?",
             "a": "Yes. Safe drinking water is available at multiple locations along the Alipiri and Srivari Mettu routes."},
            {"q": "Are toilets available on the footpath?",
             "a": "Yes. Public toilets are available at various points along both walking routes."},
            {"q": "Can senior citizens use APSRTC buses?",
             "a": "Yes. APSRTC buses are available for all pilgrims, including senior citizens."},
            {"q": "Are free buses available inside Tirumala?",
             "a": "Yes. TTD operates free 'Dharma Ratham' buses that connect important locations such as temples, cottages, choultries, bus stand, and accommodation complexes."},
            {"q": "How frequently do Dharma Ratham buses run?",
             "a": "The buses generally operate at frequent intervals, approximately every few minutes during service hours."},
            {"q": "Can I use the free bus to visit Akasa Ganga and Papavinasanam?",
             "a": "Yes. TTD free buses connect several important pilgrimage locations in Tirumala, including tourist and temple sites such as Akasa Ganga and Papavinasanam."},
            {"q": "Is parking available in Tirumala?",
             "a": "Yes. TTD provides parking facilities at designated locations for private vehicles."},
            {"q": "Is parking available near the temple?",
             "a": "Parking is available only in designated parking areas. Pilgrims should follow TTD traffic instructions."},
            {"q": "Can I travel to Tirumala at night?",
             "a": "Yes. APSRTC buses and private vehicles operate according to traffic and TTD regulations."},
            {"q": "Is walking to Tirumala safe?",
             "a": "Yes. Both footpaths are monitored with CCTV, security personnel, lighting, and medical facilities for pilgrim safety."},
        ],
    },

    "history": {
        "title": "📜 Temple History",
        "summary": (
            "*📜 Temple History*\n\n"
            "• *Lord Venkateswara* – Incarnation of Vishnu, appeared to save mankind in Kali Yuga\n"
            "• Also known as *Balaji, Srinivasa, Govinda*\n"
            "• Temple built in *Dravidian style* with gold-plated Ananda Nilayam Vimanam\n"
            "• Devotees offer *hair* as a symbol of surrender & humility\n"
            "• One of the *richest & most visited* temples in the world\n"
        ),
        "summary_te": (
            "*📜 ఆలయ చరిత్ర*\n\n"
            "• *శ్రీ వేంకటేశ్వరుడు* – కలియుగంలో మానవాళిని రక్షించడానికి వచ్చిన విష్ణువు అవతారం\n"
            "• *బాలాజీ, శ్రీనివాసుడు, గోవిందా* అనే పేర్లతో కూడా ప్రసిద్ధి\n"
            "• *ద్రావిడ శైలి*లో నిర్మించిన ఆలయం, బంగారు ఆనంద నిలయ విమానం\n"
            "• భక్తులు వినయానికి, శరణాగతికి గుర్తుగా *తలనీలాలు* సమర్పిస్తారు\n"
            "• ప్రపంచంలో అత్యంత *సంపన్న & ఎక్కువ మంది సందర్శించే* ఆలయాలలో ఒకటి\n"
        ),
        "qas": [
            {"q": "Who is Lord Venkateswara?",
             "a": "Lord Venkateswara, also known as Sri Balaji, Srinivasa, Govinda, and Venkatachalapathi, is an incarnation of Lord Vishnu who appeared in Tirumala during Kali Yuga to protect humanity and grant salvation to devotees."},
            {"q": "Why did Lord Vishnu come to Tirumala?",
             "a": "According to Hindu scriptures, Lord Vishnu descended to Tirumala as Lord Srinivasa to save mankind during Kali Yuga and to fulfill His divine promise of protecting His devotees."},
            {"q": "What is the story of Lord Venkateswara?",
             "a": "The story begins with Sage Bhrigu testing the Trimurtis. After Sage Bhrigu insulted Lord Vishnu, Goddess Lakshmi left Vaikuntha. Lord Vishnu came to Earth as Srinivasa, performed penance in Tirumala, married Goddess Padmavathi, and later manifested as Lord Venkateswara to bless devotees."},
            {"q": "Why is Tirumala called the Seven Hills?",
             "a": "Tirumala is situated on seven sacred hills known as Seshadri, Neeladri, Garudadri, Anjanadri, Vrushabhadri, Narayanadri, and Venkatadri. These hills are believed to represent the seven hoods of Adisesha."},
            {"q": "What is the importance of the Seven Hills?",
             "a": "The Seven Hills symbolize Adisesha, the divine serpent on whom Lord Vishnu rests. Lord Venkateswara resides on Venkatadri, the seventh and most sacred hill."},
            {"q": "Who built the Tirumala Temple?",
             "a": "The temple has evolved over many centuries. Various dynasties, including the Pallavas, Cholas, Pandyas, Vijayanagara rulers, and many devotees, contributed to its construction and expansion."},
            {"q": "Who was Sri Krishnadevaraya?",
             "a": "Sri Krishnadevaraya was the greatest emperor of the Vijayanagara Empire and one of the temple's most devoted patrons. He visited Tirumala several times and donated gold, jewels, land, and valuable ornaments to the temple."},
            {"q": "Who was Annamacharya?",
             "a": "Sri Tallapaka Annamacharya was a great saint-poet and devotee of Lord Venkateswara. He composed more than 32,000 devotional songs (Sankeertanas) praising the Lord."},
            {"q": "Who was Sri Ramanujacharya?",
             "a": "Sri Ramanujacharya was a renowned philosopher and spiritual leader who played a significant role in organizing temple rituals and promoting the worship of Lord Venkateswara according to the Sri Vaishnava tradition."},
            {"q": "Why is hair offered at Tirumala?",
             "a": "Pilgrims offer their hair as a symbol of humility, gratitude, and surrender to Lord Venkateswara. It represents giving up one's ego and seeking divine blessings."},
            {"q": "Why is the Tirumala Temple so famous?",
             "a": "Tirumala is one of the world's most visited pilgrimage destinations. It is renowned for its spiritual significance, ancient traditions, magnificent architecture, daily rituals, and the unwavering faith of millions of devotees."},
            {"q": "Why is Lord Venkateswara called Govinda?",
             "a": "'Govinda' is one of the sacred names of Lord Vishnu. Devotees chant 'Govinda, Govinda' while climbing the hills and during darshan as an expression of devotion and surrender."},
            {"q": "What is the significance of Varaha Swamy Temple?",
             "a": "According to tradition, devotees should first offer prayers to Sri Varaha Swamy before having darshan of Lord Venkateswara, as Lord Varaha is regarded as the original presiding deity of Tirumala."},
            {"q": "What is the significance of the Tirumala Temple architecture?",
             "a": "The temple is built in the traditional Dravidian architectural style. Its gold-plated Ananda Nilayam Vimanam, intricate carvings, ancient inscriptions, and sacred sanctum make it one of India's finest temple structures."},
            {"q": "What are some interesting facts about Tirumala Temple?",
             "a": "It is one of the richest and most visited temples in the world. Millions of pilgrims visit every year. Daily worship follows centuries-old traditions. The temple has thousands of historical inscriptions. The famous Tirupati Laddu has a Geographical Indication (GI) tag. Devotees from across the world visit the temple irrespective of language or nationality."},
        ],
    },

    "rules": {
        "title": "👕 Dress Code & Temple Rules",
        "summary": (
            "*👕 Dress Code & Temple Rules*\n\n"
            "• *Men* – Dhoti/pyjama + upper cloth or shirt\n"
            "• *Women* – Saree, half-saree, or churidar with dupatta\n"
            "• *Not allowed* – Jeans, shorts, sleeveless clothing (for most darshans)\n"
            "• *Not allowed inside* – Mobile phones, cameras, laptops, footwear, outside food\n"
            "• No alcohol, smoking, or non-veg food anywhere in Tirumala\n"
        ),
        "summary_te": (
            "*👕 దుస్తుల నియమాలు & ఆలయ నియమాలు*\n\n"
            "• *పురుషులు* – పంచె/పైజామా + పైన చొక్కా/వస్త్రం\n"
            "• *మహిళలు* – చీర, హాఫ్ చీర, లేదా చుడీదార్ + దుపట్టా\n"
            "• *అనుమతి లేదు* – జీన్స్, షార్ట్స్, స్లీవ్‌లెస్ దుస్తులు (చాలా దర్శనాలకు)\n"
            "• *లోపలికి అనుమతి లేదు* – మొబైల్, కెమెరా, ల్యాప్‌టాప్, చెప్పులు, బయటి ఆహారం\n"
            "• తిరుమలలో మద్యం, ధూమపానం, మాంసాహారం ఎక్కడా అనుమతి లేదు\n"
        ),
        "qas": [
            {"q": "What is the dress code for Tirumala Temple?",
             "a": "Devotees are expected to wear traditional Indian attire. Men should wear a dhoti or pyjama with an upper cloth/shirt, while women should wear a saree, half-saree, or churidar/salwar kameez with a dupatta."},
            {"q": "Can I wear jeans to Tirumala Temple?",
             "a": "Traditional attire is recommended. Jeans and other western casual clothing may not be permitted for certain darshan categories, and devotees are encouraged to wear traditional Indian dress while visiting the temple."},
            {"q": "Can men wear a shirt and pants?",
             "a": "For general darshan, decent full-length trousers with a shirt may be accepted in many cases. However, TTD recommends traditional attire, especially for sevas and special darshan categories."},
            {"q": "Can women wear churidar?",
             "a": "Yes. Women may wear a saree, half-saree, or churidar/salwar kameez with a dupatta."},
            {"q": "Are shorts allowed inside the temple?",
             "a": "No. Shorts, bermudas, sleeveless clothing, and other revealing outfits are not considered appropriate for temple entry."},
            {"q": "Can I carry a mobile phone?",
             "a": "Mobile phones and other electronic devices are not permitted inside the temple. Deposit them at the designated counters before entering the queue."},
            {"q": "Can I carry a camera?",
             "a": "No. Cameras and photography equipment are not allowed inside the temple premises."},
            {"q": "Can I carry a laptop?",
             "a": "Laptops are not allowed inside the temple. Deposit them at a TTD cloak room or luggage counter before joining the queue."},
            {"q": "Can I carry luggage during darshan?",
             "a": "Large bags and luggage are not permitted in the darshan queue. Use the free TTD luggage deposit facilities before entering."},
            {"q": "Are footwear and shoes allowed?",
             "a": "No. Footwear must be removed before entering the temple and queue lines. Shoe deposit counters are available."},
            {"q": "Can I carry food inside the temple?",
             "a": "Outside food and beverages should not be carried into the temple queue. Consume food before entering or use designated dining areas."},
            {"q": "Can I consume alcohol or tobacco in Tirumala?",
             "a": "No. Tirumala is a sacred pilgrimage area. Alcohol, smoking, tobacco, non-vegetarian food, and intoxicating substances are strictly prohibited."},
            {"q": "Can I take photographs inside the temple?",
             "a": "No. Photography and videography are strictly prohibited inside the temple premises."},
            {"q": "What are the important temple rules?",
             "a": "Devotees should wear traditional attire, maintain silence, follow queue instructions, respect temple customs, avoid carrying prohibited items, and cooperate with security personnel."},
            {"q": "What should I do before entering the temple?",
             "a": "Wear appropriate traditional clothing, remove footwear, deposit prohibited items such as mobile phones and luggage, carry your original photo ID and ticket (if applicable), and report at the designated time mentioned on your booking."},
        ],
    },

    "annadanam": {
        "title": "🍛 Annadanam & Laddu Information",
        "summary": (
            "*🍛 Annadanam & Laddu Information*\n\n"
            "• *Anna Prasadam* – Free meals for all pilgrims, served daily\n"
            "• Served at the *Anna Prasadam Complex*, Tirumala (+ select Tirupati spots)\n"
            "• *Tirupati Laddu* – Sacred prasadam given after darshan\n"
            "• Collect laddu using your *darshan ticket/token* at the counter\n"
            "• ₹300 ticket = 1 free laddu; extra laddus can be purchased\n"
        ),
        "summary_te": (
            "*🍛 అన్నదానం & లడ్డు సమాచారం*\n\n"
            "• *అన్న ప్రసాదం* – అందరు యాత్రికులకు ఉచిత భోజనం, ప్రతిరోజూ\n"
            "• తిరుమలలోని *అన్న ప్రసాదం కాంప్లెక్స్*లో (కొన్ని తిరుపతి ప్రదేశాల్లో కూడా)\n"
            "• *తిరుపతి లడ్డు* – దర్శనం తర్వాత ఇచ్చే పవిత్ర ప్రసాదం\n"
            "• లడ్డు కోసం మీ *దర్శన టికెట్/టోకెన్* కౌంటర్‌లో చూపించండి\n"
            "• ₹300 టికెట్‌కు 1 ఉచిత లడ్డు; అదనపు లడ్డులు కొనుగోలు చేయవచ్చు\n"
        ),
        "qas": [
            {"q": "What is Anna Prasadam?",
             "a": "Anna Prasadam is a free meal service provided by TTD to all pilgrims visiting Tirumala. It is served daily without any charge."},
            {"q": "Where is Anna Prasadam served?",
             "a": "Free Anna Prasadam is served at the Matrusri Tarigonda Vengamamba Anna Prasadam Complex in Tirumala."},
            {"q": "Is Anna Prasadam free?",
             "a": "Yes. Anna Prasadam is completely free for all pilgrims, irrespective of age, religion, or nationality."},
            {"q": "What food is served in Anna Prasadam?",
             "a": "The menu generally includes rice, sambar, rasam, curry, chutney, curd, and other vegetarian dishes. The menu may vary from day to day."},
            {"q": "What are the timings of Anna Prasadam?",
             "a": "Anna Prasadam is served throughout the day in different sessions. The timings may vary based on TTD's schedule."},
            {"q": "Can anyone eat Anna Prasadam?",
             "a": "Yes. Every pilgrim visiting Tirumala is welcome to have Anna Prasadam."},
            {"q": "Is Anna Prasadam available in Tirupati?",
             "a": "Yes. Free meals are also provided at selected TTD locations in Tirupati."},
            {"q": "What is Tirupati Laddu?",
             "a": "Tirupati Laddu is the sacred prasadam offered by TTD after darshan of Lord Venkateswara. It is one of the most famous temple prasadams in India."},
            {"q": "Where can I collect my Tirupati Laddu?",
             "a": "Laddus can be collected at the designated Laddu Distribution Counters by presenting your darshan ticket or laddu token."},
            {"q": "How many laddus do I get with a ₹300 Special Entry Darshan ticket?",
             "a": "Eligible Special Entry Darshan tickets generally include one complimentary small laddu per ticket. Additional laddus may be purchased subject to TTD rules and availability."},
            {"q": "Can I buy extra laddus?",
             "a": "Yes. Additional laddus can be purchased according to the quantity and conditions prescribed by TTD."},
            {"q": "What is required to collect laddus?",
             "a": "Carry your darshan ticket or the laddu token provided after darshan. It will be verified at the distribution counter."},
            {"q": "Can someone else collect my laddus?",
             "a": "Normally, the person holding the valid ticket or token should collect the laddus. TTD rules apply."},
            {"q": "Is the Tirupati Laddu unique?",
             "a": "Yes. Tirupati Laddu has a Geographical Indication (GI) tag, recognizing its unique preparation and association with the Tirumala Temple."},
            {"q": "Can I donate for Anna Prasadam?",
             "a": "Yes. Devotees can contribute to the Sri Venkateswara Anna Prasadam Trust through TTD's official donation channels to support the free meal service."},
        ],
    },

    "help": {
        "title": "📞 Help & Contact Information",
        "summary": (
            "*📞 Help & Contact Information*\n\n"
            "• *Website* – https://tirumala.org for bookings & info\n"
            "• *Call Centre* – For darshan, accommodation, seva queries\n"
            "• Lost child/belongings → nearest *TTD security / Police Help Desk*\n"
            "• *Medical help* – Hospitals & first-aid centres available\n"
            "• Help Desks at Tirupati, Tirumala, railway & bus stations\n"
        ),
        "summary_te": (
            "*📞 సహాయం & సంప్రదింపు వివరాలు*\n\n"
            "• *వెబ్‌సైట్* – బుకింగ్‌లు & సమాచారం కోసం https://tirumala.org\n"
            "• *కాల్ సెంటర్* – దర్శనం, వసతి, సేవల ప్రశ్నల కోసం\n"
            "• పిల్లలు/వస్తువులు పోతే → సమీప *TTD సెక్యూరిటీ / పోలీస్ హెల్ప్ డెస్క్*\n"
            "• *వైద్య సహాయం* – ఆసుపత్రులు & ఫస్ట్-ఎయిడ్ కేంద్రాలు అందుబాటులో\n"
            "• తిరుపతి, తిరుమల, రైల్వే & బస్ స్టేషన్లలో హెల్ప్ డెస్క్‌లు\n"
        ),
        "qas": [
            {"q": "How can I contact TTD?",
             "a": "You can contact TTD through its official Call Centre, website, email, or by visiting the nearest TTD Information Centre."},
            {"q": "What is the official TTD website?",
             "a": "The official website is https://tirumala.org"},
            {"q": "Where can I book darshan and accommodation online?",
             "a": "You can book darshan, accommodation, and other services through the official TTD website: https://tirumala.org"},
            {"q": "How can I contact the TTD Call Centre?",
             "a": "You can contact the official TTD Call Centre for information regarding darshan, accommodation, sevas, and other services."},
            {"q": "Does TTD have a customer care number?",
             "a": "Yes. TTD operates an official customer care service. Please refer to the latest contact information published on the official TTD website."},
            {"q": "How can I file a complaint?",
             "a": "You can submit complaints through the TTD Help Desk, official website, or designated complaint counters."},
            {"q": "How can I provide feedback?",
             "a": "Feedback can be submitted through the official TTD website or at TTD Information Centres."},
            {"q": "Where can I find the TTD Information Centre?",
             "a": "TTD Information Centres are available at Tirupati, Tirumala, and several major cities across India."},
            {"q": "What should I do if I lose my child?",
             "a": "Immediately contact the nearest TTD security personnel or Police Help Desk. Announcements and assistance will be provided to help reunite you with your child."},
            {"q": "What should I do if I lose my belongings?",
             "a": "Report the loss immediately at the nearest Lost & Found Centre or TTD Vigilance Office."},
            {"q": "Is medical assistance available?",
             "a": "Yes. TTD provides hospitals, first-aid centres, ambulances, and emergency medical services for pilgrims."},
            {"q": "Where is the nearest police station?",
             "a": "Police assistance is available throughout Tirumala and Tirupati. You can approach any police help desk or security personnel."},
            {"q": "What should I do during an emergency?",
             "a": "Stay calm and immediately contact the nearest TTD staff member, police officer, or emergency medical team."},
            {"q": "Where can I find official announcements?",
             "a": "Official announcements are published on the TTD website, official social media pages, and information centres."},
            {"q": "Does TTD have official social media accounts?",
             "a": "Yes. TTD shares important updates through its verified social media accounts. Always follow official accounts only."},
            {"q": "Can I contact TTD by email?",
             "a": "Yes. Official email addresses are available on the TTD website for various departments."},
            {"q": "Can I visit a TTD Help Desk?",
             "a": "Yes. Help Desks are available at Tirupati, Tirumala, railway stations, bus stations, and other important pilgrim locations."},
            {"q": "Where can I get information about temple services?",
             "a": "You can ask at any TTD Information Centre, Help Desk, or through the official website."},
            {"q": "Where can I get the latest TTD updates?",
             "a": "Visit the official TTD website (https://tirumala.org) or ask Sudarshan AI for the latest announcements, booking information, and important notices."},
        ],
    },
}

# ------------------------------------------------------------------
# Menu configuration — mirrors the original WhatsApp numbered menu
# ------------------------------------------------------------------

MENU_ORDER = ["darshan", "accommodation", "transport", "history", "rules", "annadanam", "help"]

# Numbers 1-7 map to category keys
CATEGORY_MAP = {str(i + 1): key for i, key in enumerate(MENU_ORDER)}

WELCOME_MESSAGE = (
    "🙏 *Welcome to Sudarshan AI*\n"
    "🛕 *TTD Pilgrim Assistant*\n\n"
    "Your AI companion for a smooth Tirumala pilgrimage.\n\n"
    "Please reply with a number:\n\n"
    "*1️⃣* 🎟️ Darshan & Tickets\n"
    "*2️⃣* 🏨 Accommodation\n"
    "*3️⃣* 🚌 Transport\n"
    "*4️⃣* 📜 Temple History\n"
    "*5️⃣* 👕 Dress Code & Temple Rules\n"
    "*6️⃣* 🍛 Annadanam & Laddu Information\n"
    "*7️⃣* 📞 Help & Contact Information\n\n"
    "💡 *Examples:*\n"
    "• Reply *1* → Darshan & Tickets\n"
    "• Reply *4* → Temple History\n\n"
    "📩 You can also just type your question directly, in English or తెలుగు, for example:\n"
    "• When will SSD tokens open?\n"
    "• Can I wear jeans?\n"
    "• శ్రీవారి చరిత్ర చెప్పండి?"
)

TELUGU_WELCOME_MESSAGE = (
    "🙏 *సుదర్శన్ AI కి స్వాగతం*\n"
    "🛕 *TTD యాత్రికుల సహాయకుడు*\n\n"
    "మీ తిరుమల యాత్రను సులభతరం చేసే AI సహాయకుడు.\n\n"
    "దయచేసి ఒక నంబర్‌తో రిప్లై ఇవ్వండి:\n\n"
    "*1️⃣* 🎟️ దర్శనం & టికెట్లు\n"
    "*2️⃣* 🏨 వసతి సౌకర్యం\n"
    "*3️⃣* 🚌 రవాణా\n"
    "*4️⃣* 📜 ఆలయ చరిత్ర\n"
    "*5️⃣* 👕 దుస్తుల నియమాలు & ఆలయ నియమాలు\n"
    "*6️⃣* 🍛 అన్నదానం & లడ్డు సమాచారం\n"
    "*7️⃣* 📞 సహాయం & సంప్రదింపు వివరాలు\n\n"
    "📩 మీరు నేరుగా మీ ప్రశ్నను తెలుగులో లేదా ఇంగ్లీష్‌లో టైప్ చేయవచ్చు."
)


def build_category_reply(category_key: str, telugu: bool = False) -> str:
    """Return a SHORT, bullet-point summary for a category (menu selection).

    This is intentionally short — it does NOT dump the full Q&A list.
    Detailed Q&A answers are only given when the pilgrim asks a specific
    question, which is handled separately by the AI (see ask_groq in app.py).
    """
    cat = KNOWLEDGE_BASE.get(category_key)
    if not cat:
        return TELUGU_WELCOME_MESSAGE if telugu else WELCOME_MESSAGE

    if telugu:
        body = cat.get("summary_te") or cat.get("summary", f"*{cat['title']}*")
        footer = "\n💬 ఈ విషయం గురించి ఏదైనా ప్రశ్న అడగండి, English లేదా తెలుగులో!"
    else:
        body = cat.get("summary") or f"*{cat['title']}*"
        footer = "\n💬 Ask me anything specific about this topic, in English or Telugu!"

    return f"{body}{footer}"


def get_full_knowledge_text() -> str:
    """Flatten the whole knowledge base into plain text for the LLM prompt."""
    chunks = []
    for key in MENU_ORDER:
        cat = KNOWLEDGE_BASE[key]
        chunks.append(f"\n## {cat['title']}")
        for qa in cat["qas"]:
            chunks.append(f"Q: {qa['q']}\nA: {qa['a']}")
    return "\n".join(chunks)
