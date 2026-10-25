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

# ==================================================================
# CONTENT UPDATE (menu answers 1, 2, 3, 4, 6, 7 + new Q&As)
# Written from TTD information given by the project owner and checked against
# official TTD announcements. Timings and quotas change often, so every answer
# points pilgrims to https://tirumala.org for the latest.
# ==================================================================

def _upsert_qa(cat, question, answer):
    """Replace the answer if the question already exists, otherwise add it."""
    qas = KNOWLEDGE_BASE[cat]["qas"]
    for qa in qas:
        if qa["q"].strip().lower() == question.strip().lower():
            qa["a"] = answer
            return
    qas.append({"q": question, "a": answer})


def _rename_qa(cat, old_q, new_q):
    for qa in KNOWLEDGE_BASE[cat]["qas"]:
        if qa["q"] == old_q:
            qa["q"] = new_q
            return


_rename_qa("annadanam", "How many laddus do I get with a ₹300 Special Entry Darshan ticket?",
           "How many laddus do I get with the ticket?")


KNOWLEDGE_BASE["darshan"]["summary"] = (
    "*🎟️ Darshan & Tickets*\n\n"
    "You can have darshan of Sri Venkateswara Swamy in these ways:\n\n"
    "*1️⃣ Free Darshan (Sarva Darshan)*\n"
    "• Free for everyone, no ticket needed. Waiting time depends on the crowd.\n\n"
    "*2️⃣ SSD Darshan (Slotted Sarva Darshan)*\n"
    "• A free token with a time slot.\n"
    "• SSD tokens are given in Tirupati at *Bhudevi Complex, Vishnu Nivasam and Srinivasam*, "
    "at the times announced by TTD.\n"
    "• Report at Tirumala at the time slot printed on your token.\n\n"
    "*3️⃣ ₹300 Special Entry Darshan*\n"
    "• Book online only, on the official TTD website or app (https://tirumala.org).\n\n"
    "*⭐ Srivani Darshan (VIP Break)*\n"
    "• ₹10,000 Srivani Trust donation + ₹500 ticket per person.\n"
    "• Only a limited number of tickets, given online and at fixed times at Tirupati Airport "
    "and Tirumala.\n\n"
    "⚠️ Book only on the official TTD website or app. Timings and quotas change, so check "
    "https://tirumala.org.\n"
)
KNOWLEDGE_BASE["darshan"]["summary_te"] = (
    "*🎟️ దర్శనం & టికెట్లు*\n\n"
    "శ్రీవారి దర్శనం ఈ విధాలుగా చేసుకోవచ్చు:\n\n"
    "*1️⃣ ఉచిత దర్శనం (సర్వ దర్శనం)*\n"
    "• అందరికీ ఉచితం, టికెట్ అవసరం లేదు. వేచి ఉండే సమయం రద్దీపై ఆధారపడి ఉంటుంది.\n\n"
    "*2️⃣ SSD దర్శనం (స్లాటెడ్ సర్వ దర్శనం)*\n"
    "• సమయం కేటాయించిన ఉచిత టోకెన్.\n"
    "• SSD టోకెన్లు తిరుపతిలోని *భూదేవి కాంప్లెక్స్, విష్ణు నివాసం, శ్రీనివాసం* వద్ద "
    "TTD ప్రకటించిన సమయాల్లో ఇస్తారు.\n"
    "• టోకెన్‌పై ఉన్న సమయానికి తిరుమలలో రిపోర్ట్ చేయాలి.\n\n"
    "*3️⃣ ₹300 ప్రత్యేక ప్రవేశ దర్శనం*\n"
    "• అధికారిక TTD వెబ్‌సైట్ లేదా యాప్‌లో (https://tirumala.org) ఆన్‌లైన్‌లో మాత్రమే బుక్ చేసుకోవాలి.\n\n"
    "*⭐ శ్రీవాణి దర్శనం (VIP బ్రేక్)*\n"
    "• ఒక్కొక్కరికి ₹10,000 శ్రీవాణి ట్రస్ట్ విరాళం + ₹500 టికెట్.\n"
    "• పరిమిత సంఖ్యలో మాత్రమే: ఆన్‌లైన్‌లో, తిరుపతి విమానాశ్రయం మరియు తిరుమలలో నిర్ణీత సమయాల్లో.\n\n"
    "⚠️ అధికారిక TTD వెబ్‌సైట్ / యాప్‌లో మాత్రమే బుక్ చేయండి. సమయాలు, కోటాలు మారుతుంటాయి, "
    "https://tirumala.org చూడండి.\n"
)

KNOWLEDGE_BASE["accommodation"]["summary"] = (
    "*🏨 Accommodation*\n\n"
    "TTD provides stay in its own complexes (choultries):\n\n"
    "*In Tirupati*\n"
    "• *Vishnu Nivasam* – opposite Tirupati Railway Station\n"
    "• *Srinivasam* – opposite Tirupati bus stand (RTC)\n"
    "• *Bhudevi Complex* – near Alipiri\n\n"
    "*In Tirumala (on the hills)*\n"
    "• *Madhava Nilayam* – opposite Tirumala bus stand\n\n"
    "• Rest halls, lockers and bathing facilities are available (subject to availability).\n"
    "• Rooms: book on the official TTD website or app, or at the current-booking counters "
    "when available.\n"
)
KNOWLEDGE_BASE["accommodation"]["summary_te"] = (
    "*🏨 వసతి*\n\n"
    "TTD తన సొంత సముదాయాల్లో (చౌల్ట్రీలు) వసతి కల్పిస్తుంది:\n\n"
    "*తిరుపతిలో*\n"
    "• *విష్ణు నివాసం* – తిరుపతి రైల్వే స్టేషన్ ఎదురుగా\n"
    "• *శ్రీనివాసం* – తిరుపతి బస్ స్టాండ్ (RTC) ఎదురుగా\n"
    "• *భూదేవి కాంప్లెక్స్* – అలిపిరి సమీపంలో\n\n"
    "*తిరుమలలో (కొండపై)*\n"
    "• *మాధవ నిలయం* – తిరుమల బస్ స్టాండ్ ఎదురుగా\n\n"
    "• విశ్రాంతి హాళ్లు, లాకర్లు, స్నాన సౌకర్యాలు అందుబాటులో ఉంటాయి (లభ్యతను బట్టి).\n"
    "• గదులు: అధికారిక TTD వెబ్‌సైట్ / యాప్‌లో బుక్ చేయండి, లేదా అందుబాటులో ఉన్నప్పుడు "
    "కరెంట్ బుకింగ్ కౌంటర్ల వద్ద.\n"
)

KNOWLEDGE_BASE["transport"]["summary"] = (
    "*🚌 Transportation*\n\n"
    "*In Tirupati*\n"
    "• TTD runs *free buses* from Tirupati Railway Station to the *Srivari Mettu* / Alipiri footpath.\n"
    "• APSRTC buses run from Tirupati to Tirumala frequently. Taxis and autos are also available.\n\n"
    "*Walking routes to Tirumala*\n"
    "• *Srivari Mettu* – about 2.4 km (shorter)\n"
    "• *Alipiri* – about 11 km (traditional route)\n\n"
    "*In Tirumala*\n"
    "• TTD runs *free buses* (Dharma Ratham) between the temple, cottages, choultries and "
    "sightseeing points.\n\n"
    "*Own vehicle:* allowed after the Alipiri check post.\n"
)
KNOWLEDGE_BASE["transport"]["summary_te"] = (
    "*🚌 రవాణా*\n\n"
    "*తిరుపతిలో*\n"
    "• రైల్వే స్టేషన్ నుండి *శ్రీవారి మెట్టు* / అలిపిరి నడక మార్గానికి TTD *ఉచిత బస్సులు* నడుపుతుంది.\n"
    "• తిరుపతి నుండి తిరుమలకు APSRTC బస్సులు తరచుగా ఉంటాయి. టాక్సీలు, ఆటోలు కూడా దొరుకుతాయి.\n\n"
    "*తిరుమలకు నడక మార్గాలు*\n"
    "• *శ్రీవారి మెట్టు* – సుమారు 2.4 కి.మీ (తక్కువ దూరం)\n"
    "• *అలిపిరి* – సుమారు 11 కి.మీ (సంప్రదాయ మార్గం)\n\n"
    "*తిరుమలలో*\n"
    "• ఆలయం, కాటేజీలు, చౌల్ట్రీలు, దర్శనీయ స్థలాల మధ్య TTD *ఉచిత బస్సులు* (ధర్మ రథం) నడుపుతుంది.\n\n"
    "*సొంత వాహనం:* అలిపిరి చెక్‌పోస్ట్ తనిఖీ తర్వాత అనుమతిస్తారు.\n"
)

KNOWLEDGE_BASE["history"]["summary"] = (
    "*📜 Temple History*\n\n"
    "• Sri Venkateswara Swamy (Balaji, Srinivasa, Govinda) is Lord Vishnu, who came to Earth "
    "in Kali Yuga to protect devotees.\n"
    "• The temple stands on the *Seven Hills* of Tirumala. The hills are believed to be the "
    "form of Adisesha.\n"
    "• Many dynasties – Pallavas, Cholas, Pandyas and the Vijayanagara kings, including "
    "Sri Krishnadevaraya – served the temple over the centuries.\n"
    "• Saint Annamacharya composed more than 32,000 songs on the Lord. Sri Ramanujacharya "
    "helped organise the temple's worship traditions.\n"
    "• It is built in the Dravidian style, with the golden *Ananda Nilayam Vimanam* over the sanctum.\n"
    "• Devotees offer their hair as a sign of surrender and chant \"Govinda!\".\n"
    "• It is one of the most visited temples in the world.\n"
)
KNOWLEDGE_BASE["history"]["summary_te"] = (
    "*📜 ఆలయ చరిత్ర*\n\n"
    "• శ్రీ వేంకటేశ్వర స్వామి (బాలాజీ, శ్రీనివాసుడు, గోవిందుడు) కలియుగంలో భక్తులను రక్షించడానికి "
    "భూమిపై వెలసిన శ్రీ మహావిష్ణువు.\n"
    "• ఆలయం తిరుమలలోని *సప్తగిరులపై* ఉంది. ఈ కొండలు ఆదిశేషుని రూపంగా భావిస్తారు.\n"
    "• పల్లవులు, చోళులు, పాండ్యులు, విజయనగర రాజులు (శ్రీ కృష్ణదేవరాయలు సహా) శతాబ్దాలుగా "
    "ఆలయానికి సేవ చేశారు.\n"
    "• అన్నమయ్య 32,000కు పైగా సంకీర్తనలు స్వామివారిపై రచించారు. శ్రీ రామానుజాచార్యులు "
    "ఆలయ ఆరాధనా సంప్రదాయాలను క్రమబద్ధం చేయడంలో తోడ్పడ్డారు.\n"
    "• ద్రావిడ శైలిలో నిర్మితమైన ఈ ఆలయంలో గర్భగుడిపై బంగారు *ఆనంద నిలయం విమానం* ఉంది.\n"
    "• భక్తులు శరణాగతికి గుర్తుగా తలనీలాలు సమర్పించి \"గోవిందా!\" అని స్మరిస్తారు.\n"
    "• ప్రపంచంలో అత్యధికంగా సందర్శించే ఆలయాల్లో ఇది ఒకటి.\n"
)

KNOWLEDGE_BASE["annadanam"]["summary"] = (
    "*🍛 Annadanam & Laddu*\n\n"
    "*🍛 Free meals (Anna Prasadam)*\n"
    "• Free for all pilgrims.\n"
    "• *In Tirumala:* the main centre is the *Matrusri Tarigonda Vengamamba Anna Prasadam "
    "Complex*. Free meals are also served at *Madhava Nilayam*.\n"
    "• *In Tirupati:* at *Vishnu Nivasam* and *Srinivasam*.\n"
    "• Timings change, so check https://tirumala.org.\n\n"
    "*🍬 Laddu*\n"
    "• Everyone who has darshan – free darshan, SSD token or a ticket – gets *one free laddu*.\n"
    "• Collect it at the laddu counter after darshan with your ticket or token.\n"
    "• Extra laddus can be bought at the counters.\n"
)
KNOWLEDGE_BASE["annadanam"]["summary_te"] = (
    "*🍛 అన్నదానం & లడ్డు*\n\n"
    "*🍛 ఉచిత భోజనం (అన్న ప్రసాదం)*\n"
    "• యాత్రికులందరికీ ఉచితం.\n"
    "• *తిరుమలలో:* ప్రధాన కేంద్రం *మాతృశ్రీ తరిగొండ వెంగమాంబ అన్న ప్రసాద సముదాయం*. "
    "*మాధవ నిలయం* వద్ద కూడా ఉచిత భోజనం ఉంది.\n"
    "• *తిరుపతిలో:* *విష్ణు నివాసం*, *శ్రీనివాసం* వద్ద.\n"
    "• సమయాలు మారుతుంటాయి, https://tirumala.org చూడండి.\n\n"
    "*🍬 లడ్డు*\n"
    "• దర్శనం చేసుకున్న ప్రతి ఒక్కరికి (ఉచిత దర్శనం, SSD టోకెన్ లేదా టికెట్) *ఒక లడ్డు ఉచితం*.\n"
    "• దర్శనం తర్వాత టికెట్ / టోకెన్‌తో లడ్డు కౌంటర్ వద్ద తీసుకోండి.\n"
    "• అదనపు లడ్డూలను కౌంటర్ల వద్ద కొనుగోలు చేయవచ్చు.\n"
)

KNOWLEDGE_BASE["help"]["summary"] = (
    "*📞 Help & Contact Information*\n\n"
    "• *TTD Call Centre (24x7, toll-free):* 155257\n"
    "• *Toll-free:* 1800 425 4141\n"
    "• *Helpline:* 0877-2233333 / 0877-2277777\n"
    "• *Website & app:* https://tirumala.org  |  app name: TTDevasthanams\n"
    "• *Help desks* at Tirupati, Tirumala, and the railway and bus stations.\n"
    "• Lost child, lost belongings or emergency: go to the nearest TTD security / police help desk.\n"
    "• ⚠️ Beware of fake websites and agents. Book only on the official website or app, and "
    "report fraud on 155257.\n\n"
    "To register a complaint with TTD, reply *C*.\n"
)
KNOWLEDGE_BASE["help"]["summary_te"] = (
    "*📞 సహాయం & సంప్రదింపు వివరాలు*\n\n"
    "• *TTD కాల్ సెంటర్ (24x7, టోల్-ఫ్రీ):* 155257\n"
    "• *టోల్-ఫ్రీ:* 1800 425 4141\n"
    "• *హెల్ప్‌లైన్:* 0877-2233333 / 0877-2277777\n"
    "• *వెబ్‌సైట్ & యాప్:* https://tirumala.org  |  యాప్: TTDevasthanams\n"
    "• తిరుపతి, తిరుమల, రైల్వే మరియు బస్ స్టేషన్లలో *హెల్ప్ డెస్క్‌లు*.\n"
    "• తప్పిపోయిన పిల్లలు, వస్తువులు లేదా అత్యవసరం: సమీప TTD సెక్యూరిటీ / పోలీస్ హెల్ప్ డెస్క్‌కు వెళ్లండి.\n"
    "• ⚠️ నకిలీ వెబ్‌సైట్లు, ఏజెంట్లతో జాగ్రత్త. అధికారిక వెబ్‌సైట్ / యాప్‌లోనే బుక్ చేయండి, "
    "మోసాన్ని 155257కు తెలియజేయండి.\n\n"
    "TTDకి ఫిర్యాదు నమోదు చేయడానికి *C* పంపండి.\n"
)

# ---------------- Darshan Q&As ----------------
_upsert_qa("darshan", "What are the different types of darshan?",
    "There are three main ways to have darshan:\n"
    "1. Free Darshan (Sarva Darshan) – free for everyone, no ticket.\n"
    "2. SSD Darshan (Slotted Sarva Darshan) – a free token with a time slot. SSD tokens are given at "
    "Bhudevi Complex, Vishnu Nivasam and Srinivasam in Tirupati at the times TTD announces.\n"
    "3. ₹300 Special Entry Darshan – book online on the official TTD website or app.\n"
    "There is also Srivani (VIP Break) Darshan for a ₹10,000 Srivani Trust donation plus a ₹500 ticket. "
    "Senior citizen and differently abled devotees have special arrangements. Check https://tirumala.org for the latest.")
_upsert_qa("darshan", "What is the meaning of SSD? What is SSD full form?",
    "SSD means Slotted Sarva Darshan. It is a free darshan: you collect an SSD token that gives you a time "
    "slot, and you report at Tirumala at that time instead of waiting in a long queue. SSD tokens are given in "
    "Tirupati at Bhudevi Complex, Vishnu Nivasam and Srinivasam. The token timings and the number of tokens change, "
    "so check https://tirumala.org.")
_upsert_qa("darshan", "Where can I get SSD tokens? Where are SSD tokens given?",
    "SSD tokens are given in Tirupati at Bhudevi Complex, Vishnu Nivasam (opposite the railway station) and "
    "Srinivasam (opposite the bus stand), at the times announced by TTD. Only a limited number of tokens are "
    "given, so check https://tirumala.org for the latest timings.")
_upsert_qa("darshan", "How can I reach Tirumala after taking SSD token?",
    "After taking your SSD token in Tirupati, go up to Tirumala by APSRTC bus, taxi or your own vehicle, or walk "
    "through Srivari Mettu (about 2.4 km) or Alipiri (about 11 km). Reach Tirumala in time and report at the "
    "darshan entry at the time slot printed on your token. Carry the token and your original photo ID. If you "
    "are unsure where to report, ask any TTD staff or a help desk at Tirumala.")
_upsert_qa("darshan", "What should I do after getting SSD token? When should I report at Tirumala?",
    "Report at Tirumala at the time slot printed on your SSD token. Reach in good time, because entry after your "
    "slot depends on TTD's policy. Carry the token and your original photo ID. After darshan you get one free laddu.")
_upsert_qa("darshan", "How do I book a darshan ticket?",
    "Book on the official TTD website or app only (https://tirumala.org): register or log in, choose the date "
    "and slot, add the pilgrims' details and pay online.\n"
    "• ₹300 Special Entry Darshan: online booking only, on dates announced by TTD.\n"
    "• SSD tokens: free, given at Bhudevi Complex, Vishnu Nivasam and Srinivasam in Tirupati.\n"
    "• Srivani: ₹10,000 donation + ₹500 ticket, online and at fixed times at Tirupati Airport and Tirumala.\n"
    "Do not book through agents or unknown websites.")
_upsert_qa("darshan", "What is Special Entry Darshan?",
    "Special Entry Darshan costs ₹300 per person. Book it online only, on the official TTD website or app "
    "(https://tirumala.org), subject to slot availability. Release dates are announced by TTD, so check the "
    "website or app for the latest. Do not book through agents or unknown websites.")
_upsert_qa("darshan", "What is Srivani darshan ticket? How much does Srivani ticket cost?",
    "Srivani Darshan (VIP Break Darshan) needs a ₹10,000 donation to the Srivani Trust plus a ₹500 darshan ticket "
    "for each person. Only a limited number of tickets are given, online and at fixed times at Tirupati Airport "
    "and Tirumala. TTD changes the quota and timings often, so check https://tirumala.org.")
_upsert_qa("darshan", "Where can I get Srivani ticket? Srivani darshan counter",
    "Srivani tickets are available online on the official TTD website or app, at the Srivani counter at Tirupati "
    "Airport, and at Tirumala at fixed times. Only a limited number of tokens are given each day, so check "
    "https://tirumala.org for the current quota and timings.")

_upsert_qa("darshan", "Is VIP Darshan available?",
    "VIP Darshan follows TTD's official eligibility rules. The option open to the public is Srivani (VIP Break) "
    "Darshan: a ₹10,000 Srivani Trust donation plus a ₹500 ticket per person, with a limited number of tickets "
    "online and at fixed times at Tirupati Airport and Tirumala. Check https://tirumala.org for the latest.")

# ---------------- Accommodation Q&As ----------------
_upsert_qa("accommodation", "Does TTD provide free accommodation?",
    "Yes. TTD provides rest halls, dormitories and rooms in its own complexes (choultries): Vishnu Nivasam, "
    "Srinivasam and Bhudevi Complex in Tirupati, and Madhava Nilayam at Tirumala. Availability depends on the "
    "rush; rooms can be booked on the official TTD website or app.")
_upsert_qa("accommodation", "Which TTD choultries and accommodation complexes are in Tirupati and Tirumala?",
    "In Tirupati: Vishnu Nivasam (opposite the railway station), Srinivasam (opposite the bus stand) and "
    "Bhudevi Complex (near Alipiri). In Tirumala: Madhava Nilayam (opposite the Tirumala bus stand).")
_upsert_qa("accommodation", "Where is Srinivasam?",
    "Srinivasam is a TTD pilgrim complex in Tirupati, opposite the Tirupati RTC bus stand. It has rest halls, "
    "lockers and bathing facilities, gives out SSD tokens, and serves free Anna Prasadam.")
_upsert_qa("accommodation", "What is Bhudevi Complex? Where is Bhudevi Complex located?",
    "Bhudevi Complex is a TTD pilgrim complex in Tirupati, near Alipiri. It is one of the places where SSD "
    "tokens are given.")

# ---------------- Transport Q&As ----------------
_upsert_qa("transport", "How to reach Srivari Mettu footpath?",
    "TTD runs free buses from Tirupati Railway Station to the Srivari Mettu footpath. From there you can walk "
    "about 2.4 km up to Tirumala. (Alipiri, about 11 km, is the other walking route.)")

# ---------------- Annadanam & laddu Q&As ----------------
_upsert_qa("annadanam", "Where can I get free food? Location of free food",
    "Free food (Anna Prasadam) is served at these places:\n"
    "• Tirumala: Matrusri Tarigonda Vengamamba Anna Prasadam Complex (main centre) and Madhava Nilayam.\n"
    "• Tirupati: Vishnu Nivasam (opposite the railway station) and Srinivasam (opposite the bus stand).\n"
    "It is free for all pilgrims. Timings change, so check https://tirumala.org.")
_upsert_qa("annadanam", "Is Anna Prasadam available in Tirupati?",
    "Yes. Free meals are served at Vishnu Nivasam (opposite Tirupati Railway Station) and Srinivasam "
    "(opposite the Tirupati bus stand).")
_upsert_qa("annadanam", "Where is Anna Prasadam served?",
    "In Tirumala, free Anna Prasadam is served at the Matrusri Tarigonda Vengamamba Anna Prasadam Complex "
    "(the main centre) and at Madhava Nilayam. In Tirupati it is served at Vishnu Nivasam and Srinivasam.")
_upsert_qa("annadanam", "Do I get a free laddu with free darshan or SSD token?",
    "Yes. Every pilgrim who has darshan – free darshan, SSD token or a ticket – gets one free laddu. Collect it "
    "at the laddu counter after darshan with your ticket or token. Extra laddus can be bought.")

_upsert_qa("annadanam", "Is Anna Prasadam free?",
    "Yes. Anna Prasadam is completely free for all pilgrims, irrespective of age, religion or nationality. "
    "In Tirumala it is served at the Matrusri Tarigonda Vengamamba Anna Prasadam Complex (main centre) and at "
    "Madhava Nilayam. In Tirupati it is served at Vishnu Nivasam and Srinivasam.")
_upsert_qa("annadanam", "What is Anna Prasadam?",
    "Anna Prasadam is the free meal service of TTD for all pilgrims. In Tirumala it is served at the Matrusri "
    "Tarigonda Vengamamba Anna Prasadam Complex and at Madhava Nilayam. In Tirupati it is served at Vishnu "
    "Nivasam and Srinivasam. Timings change, so check https://tirumala.org.")

# ---------------- Help & contact Q&As ----------------
_upsert_qa("help", "What is the TTD helpline number?",
    "TTD Call Centre (24x7, toll-free): 155257. Toll-free: 1800 425 4141. Helpline: 0877-2233333 or "
    "0877-2277777. Website and app: https://tirumala.org (app name: TTDevasthanams).")
_upsert_qa("help", "How can I contact the TTD Call Centre?",
    "Call the TTD Call Centre toll-free on 155257 (24x7), or 1800 425 4141. You can also call 0877-2233333 or "
    "0877-2277777, or visit https://tirumala.org.")
_upsert_qa("help", "Does TTD have a customer care number?",
    "Yes. TTD Call Centre (24x7, toll-free): 155257. Toll-free: 1800 425 4141. Helpline: 0877-2233333 / 0877-2277777.")
_upsert_qa("help", "How can I contact TTD?",
    "Call the TTD Call Centre on 155257 (toll-free, 24x7) or 1800 425 4141, call 0877-2233333 / 0877-2277777, "
    "visit https://tirumala.org, or go to any TTD help desk or information centre in Tirupati or Tirumala.")
_upsert_qa("help", "How can I report a fraud or a fake website?",
    "Book only on the official TTD website or app (https://tirumala.org). If someone asks for money for darshan "
    "or rooms, or a website looks fake, report it on the TTD toll-free number 155257. You can also reply *C* here "
    "to register a complaint.")


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
    """Flatten the whole knowledge base into plain text for the LLM prompt.

    NOTE: This is kept for reference/debugging, but is NOT used on the hot
    webhook path anymore — sending the full ~24,000-character knowledge base
    on every single message used ~6,000+ tokens per request and triggered
    Groq's free-tier "429 Too Many Requests" rate limit. Use
    get_relevant_knowledge_text() instead, which sends only a handful of
    matching Q&As per question.
    """
    chunks = []
    for key in MENU_ORDER:
        cat = KNOWLEDGE_BASE[key]
        chunks.append(f"\n## {cat['title']}")
        for qa in cat["qas"]:
            chunks.append(f"Q: {qa['q']}\nA: {qa['a']}")
    return "\n".join(chunks)


# ------------------------------------------------------------------
# Base word-matching helpers (the foundation the keyword/synonym engine
# below builds on).
# ------------------------------------------------------------------

_QA_INDEX = [
    (key, qa["q"], qa["a"])
    for key in MENU_ORDER
    for qa in KNOWLEDGE_BASE[key]["qas"]
]

_STOPWORDS = {
    "the", "is", "are", "a", "an", "to", "for", "of", "in", "on", "at",
    "and", "or", "do", "does", "can", "i", "my", "me", "what", "how",
    "where", "when", "who", "will", "should", "would", "please", "with",
    # Domain-generic words that appear in almost EVERY pilgrim question —
    # they carry no discriminating power for matching, so counting them
    # only dilutes the confidence score and causes near-miss questions
    # (e.g. "Can I wear jeans?" vs "Can I wear jeans to Tirumala Temple?")
    # to fall just short of the direct-match threshold.
    "tirumala", "tirupati", "temple", "ttd", "swami", "swamy", "swamivaru",
    "lord", "sri", "devasthanam", "devasthanams",
}


def _word_set(text: str) -> set:
    """Lowercase, strip punctuation, split into words, drop stopwords/short
    words. Works fine on Telugu script too since we only split on
    non-alphanumeric characters (Telugu letters count as alphanumeric)."""
    words = "".join(ch if ch.isalnum() else " " for ch in text.lower()).split()
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


# ==================================================================
# KEYWORD SYNONYM DICTIONARY (English + Telugu, kept SEPARATE per concept)
# ==================================================================
# This is the main cost-reduction engine. Every concept a pilgrim might ask
# about is mapped to a bundle of English AND Telugu phrases people actually
# type on WhatsApp (including common misspellings / Romanized Telugu).
#
# How it helps:
#   1. A Telugu-typed question can now match an English-only Q&A/answer,
#      because we expand the query with the English side of any concept
#      whose Telugu side appears in the question (and vice versa).
#   2. When the expanded match is confident enough, we skip Groq COMPLETELY
#      and answer straight from the knowledge base — zero API cost.
#   3. When we DO need Groq (no confident match), the extra keywords still
#      make search_relevant_qas() pick better, smaller context — fewer
#      tokens per call than plain word-matching alone.
#
# To add more coverage later: just add more phrases to any concept below,
# or add a brand-new concept block. No other code needs to change.
# ------------------------------------------------------------------

KEYWORD_SYNONYMS = {

    "darshan_general": {
        "en": ["darshan", "viewing", "see swamy", "see god", "see lord",
               "have darshan", "temple visit", "darshanam", "swamy varu"],
        "te": ["దర్శనం", "దర్శన", "స్వామి దర్శనం", "భగవంతుని దర్శనం",
               "దేవుని దర్శనం", "దర్శనము", "స్వామివారి దర్శనం"],
    },
    "sarva_darshan": {
        "en": ["sarva darshan", "free darshan", "general darshan",
               "normal darshan", "regular darshan"],
        "te": ["సర్వ దర్శనం", "ఉచిత దర్శనం", "సాధారణ దర్శనం"],
    },
    "special_entry": {
        "en": ["special entry", "300 rupees ticket", "rs 300 ticket",
               "paid darshan", "300 ticket"],
        "te": ["స్పెషల్ ఎంట్రీ", "300 రూపాయల టికెట్", "చెల్లింపు దర్శనం"],
    },
    "divya_darshan": {
        "en": ["divya darshan", "footpath darshan", "walking darshan"],
        "te": ["దివ్య దర్శనం", "కాలినడక దర్శనం", "నడక దర్శనం"],
    },
    "senior_citizen": {
        "en": ["senior citizen", "old age", "elderly", "senior citizen darshan",
               "old people", "aged"],
        "te": ["సీనియర్ సిటిజన్", "వృద్ధులు", "పెద్దవారు", "వయసు మళ్లిన వారు"],
    },
    "differently_abled": {
        "en": ["differently abled", "disabled", "handicapped", "wheelchair",
               "special needs", "physically challenged"],
        "te": ["దివ్యాంగులు", "వికలాంగులు", "అంగవైకల్యం", "వీల్‌చైర్"],
    },
    "ticket_booking": {
        "en": ["ticket", "tickets", "booking", "book online", "reserve",
               "slot", "quota", "book darshan", "how to book"],
        "te": ["టికెట్", "టికెట్లు", "బుకింగ్", "బుక్ చేయడం", "స్లాట్",
               "కోటా", "ఎలా బుక్ చేయాలి"],
    },
    "token": {
        "en": ["token", "ssd", "ssd token", "ssd ticket", "token release", "token timing",
               "tokens open", "token date"],
        "te": ["టోకెన్", "SSD టోకెన్", "టోకెన్ ఎప్పుడు"],
    },
    "ssd_meaning": {
        "en": ["what is ssd", "ssd meaning", "ssd means", "meaning of ssd", "ssd full form",
               "full form of ssd", "what does ssd mean", "ssd mean"],
        "te": ["SSD అంటే ఏమిటి", "ఎస్ఎస్డి అంటే"],
    },
    "srivani": {
        "en": ["srivani", "sri vani", "vip break darshan", "break darshan"],
        "te": ["శ్రీవాణి", "వీఐపీ బ్రేక్ దర్శనం"],
    },
    "cancellation": {
        "en": ["cancel", "cancellation", "refund", "reschedule",
               "change date", "modify booking"],
        "te": ["రద్దు", "వాపసు", "రీషెడ్యూల్", "తేదీ మార్పు", "బుకింగ్ మార్చడం"],
    },
    "id_proof": {
        "en": ["id proof", "aadhaar", "photo id", "identity card",
               "document required", "govt id"],
        "te": ["గుర్తింపు కార్డు", "ఆధార్", "ఫోటో ఐడి", "పత్రం", "గుర్తింపు పత్రం"],
    },
    "qr_code": {
        "en": ["qr code", "scan code", "barcode"],
        "te": ["క్యూఆర్ కోడ్", "స్కాన్", "బార్‌కోడ్"],
    },
    "waiting_time": {
        "en": ["waiting time", "queue", "crowd", "rush", "how long wait",
               "line", "how many hours"],
        "te": ["వేచి ఉండే సమయం", "క్యూ", "రద్దీ", "ఎంత సమయం", "లైన్"],
    },
    "accommodation_general": {
        "en": ["accommodation", "stay", "room", "lodging", "hotel",
               "rest house", "free stay", "where to stay"],
        "te": ["వసతి", "బస", "గది", "రూమ్", "ఉచిత బస", "ఎక్కడ ఉండాలి"],
    },
    "vishnu_nivasam": {
        "en": ["vishnu nivasam"],
        "te": ["విష్ణు నివాసం"],
    },
    "madhava_nilayam": {
        "en": ["madhava nilayam"],
        "te": ["మాధవ నిలయం"],
    },
    "locker": {
        "en": ["locker", "luggage storage", "safe deposit", "keep luggage"],
        "te": ["లాకర్", "సామాను భద్రపరచడం", "లగేజీ దాచడం"],
    },
    "bathing": {
        "en": ["bath", "bathing", "shower", "toilet", "restroom", "washroom"],
        "te": ["స్నానం", "టాయిలెట్", "బాత్రూమ్", "స్నానాల గది"],
    },
    "transport_general": {
        "en": ["transport", "travel", "how to reach", "how to go",
               "commute", "get to tirumala", "best way to travel"],
        "te": ["రవాణా", "ప్రయాణం", "ఎలా వెళ్ళాలి", "ఎలా చేరుకోవాలి"],
    },
    "bus": {
        "en": ["bus", "apsrtc", "bus stand", "bus timings", "bus service"],
        "te": ["బస్సు", "APSRTC", "బస్ స్టాండ్", "బస్సు సమయాలు"],
    },
    "taxi": {
        "en": ["taxi", "cab", "auto rickshaw", "private vehicle", "car",
               "own vehicle", "hire taxi"],
        "te": ["టాక్సీ", "క్యాబ్", "ఆటో", "సొంత వాహనం", "కారు"],
    },
    "train": {
        "en": ["train", "railway station", "railway"],
        "te": ["రైలు", "రైల్వే స్టేషన్"],
    },
    "flight": {
        "en": ["flight", "airport", "air travel", "by air"],
        "te": ["విమానం", "విమానాశ్రయం"],
    },
    "footpath": {
        "en": ["footpath", "walking route", "alipiri", "srivari mettu",
               "steps", "trek", "walking path", "hike"],
        "te": ["కాలిబాట", "నడక మార్గం", "అలిపిరి", "శ్రీవారి మెట్టు", "మెట్లు"],
    },
    "parking": {
        "en": ["parking", "park vehicle", "car parking"],
        "te": ["పార్కింగ్", "వాహనం నిలపడం"],
    },
    "dharma_ratham": {
        "en": ["dharma ratham", "free bus inside tirumala", "local bus",
               "shuttle bus"],
        "te": ["ధర్మ రథం", "ఉచిత బస్సు", "లోకల్ బస్సు"],
    },
    "temple_history": {
        "en": ["history", "legend", "story", "mythology", "origin",
               "temple history", "why famous"],
        "te": ["చరిత్ర", "పురాణం", "కథ", "మూలం", "ఆలయ చరిత్ర"],
    },
    "venkateswara": {
        "en": ["venkateswara", "balaji", "srinivasa", "govinda",
               "lord vishnu", "who is venkateswara"],
        "te": ["వేంకటేశ్వరుడు", "బాలాజీ", "శ్రీనివాసుడు", "గోవిందా", "విష్ణువు"],
    },
    "annamacharya": {
        "en": ["annamacharya", "saint poet", "sankeertana"],
        "te": ["అన్నమాచార్య", "సంకీర్తన"],
    },
    "temple_architecture": {
        "en": ["architecture", "vimanam", "gold roof", "gopuram", "structure"],
        "te": ["నిర్మాణశైలి", "విమానం", "బంగారు కప్పు", "గోపురం"],
    },
    "tonsure": {
        "en": ["tonsure", "hair offering", "shave head", "mottai", "haircut"],
        "te": ["తలనీలాలు", "క్షురకర్మ", "గుండు", "జుట్టు సమర్పణ"],
    },
    "dress_code": {
        "en": ["dress code", "what to wear", "clothing", "attire",
               "traditional dress", "dress rules"],
        "te": ["దుస్తుల నియమాలు", "ఏమి ధరించాలి", "వస్త్రధారణ",
               "సంప్రదాయ దుస్తులు"],
    },
    "jeans_shorts": {
        "en": ["jeans", "shorts", "pants", "trousers", "western clothes",
               "can i wear jeans"],
        "te": ["జీన్స్", "షార్ట్స్", "పాంట్లు", "పాశ్చాత్య దుస్తులు"],
    },
    "mobile_camera": {
        "en": ["mobile phone", "camera", "photography", "video",
               "electronic device", "phone allowed"],
        "te": ["మొబైల్ ఫోన్", "కెమెరా", "ఫోటోగ్రఫీ", "వీడియో", "ఎలక్ట్రానిక్ పరికరం"],
    },
    "footwear": {
        "en": ["footwear", "shoes", "chappals", "slippers", "sandals"],
        "te": ["చెప్పులు", "బూట్లు", "సాండల్స్"],
    },
    "prohibited_items": {
        "en": ["not allowed", "prohibited", "banned items", "restricted",
               "what can i carry"],
        "te": ["అనుమతి లేదు", "నిషేధించబడింది", "నిషేధిత వస్తువులు"],
    },
    "food_rules": {
        "en": ["food", "alcohol", "smoking", "non veg", "tobacco",
               "drinking", "eat inside"],
        "te": ["ఆహారం", "మద్యం", "ధూమపానం", "మాంసాహారం", "పొగాకు"],
    },
    "temple_rules_general": {
        "en": ["rules", "regulations", "guidelines", "discipline", "conduct",
               "temple rules"],
        "te": ["నియమాలు", "నిబంధనలు", "మార్గదర్శకాలు", "క్రమశిక్షణ"],
    },
    "anna_prasadam": {
        "en": ["anna prasadam", "free food", "free meal", "prasadam meal",
               "annadanam"],
        "te": ["అన్న ప్రసాదం", "ఉచిత భోజనం", "ప్రసాదం", "అన్నదానం"],
    },
    "laddu": {
        "en": ["laddu", "prasadam sweet", "tirupati laddu", "sweet prasadam"],
        "te": ["లడ్డు", "ప్రసాదం", "తిరుపతి లడ్డు", "మధురం"],
    },
    "help_contact": {
        "en": ["help", "contact", "phone number", "helpline",
               "call centre", "customer care", "contact number"],
        "te": ["సహాయం", "సంప్రదింపు", "ఫోన్ నంబర్", "హెల్ప్‌లైన్",
               "కాల్ సెంటర్"],
    },
    "complaint": {
        "en": ["complaint", "feedback", "grievance", "file complaint"],
        "te": ["ఫిర్యాదు", "అభిప్రాయం", "వ్యాజ్యం"],
    },
    "lost_found": {
        "en": ["lost", "missing", "found", "lost child", "lost belongings",
               "lost item"],
        "te": ["పోయింది", "తప్పిపోయింది", "దొరికింది", "పిల్లవాడు తప్పిపోయాడు"],
    },
    "medical": {
        "en": ["medical", "hospital", "first aid", "ambulance",
               "emergency", "doctor", "sick", "health"],
        "te": ["వైద్యం", "ఆసుపత్రి", "ప్రథమ చికిత్స", "అంబులెన్స్",
               "అత్యవసరం", "డాక్టర్"],
    },
    "police_security": {
        "en": ["police", "security", "safety"],
        "te": ["పోలీసు", "భద్రత", "రక్షణ"],
    },
    "website_online": {
        "en": ["website", "online", "official site", "app", "portal"],
        "te": ["వెబ్‌సైట్", "ఆన్‌లైన్", "అధికారిక సైట్", "యాప్"],
    },
}

# Flatten into (phrase, concept_key) pairs, longest phrases first so
# multi-word phrases (e.g. "special entry") are matched before a shorter
# phrase that might be a substring of it.
_ALL_SYNONYM_PHRASES = sorted(
    (
        (phrase.lower(), concept)
        for concept, langs in KEYWORD_SYNONYMS.items()
        for lang_list in langs.values()
        for phrase in lang_list
    ),
    key=lambda item: -len(item[0]),
)


def expand_query_concepts(query: str) -> set:
    """Return the set of concept keys detected in the query, using TWO
    matching strategies:

    1) Substring match — fast, and correct for single strong words or
       Telugu compound phrases (e.g. "అన్న ప్రసాదం" typed exactly).
    2) Order-independent word-subset match — a multi-word EN/TE phrase
       counts as matched if ALL of its significant words appear SOMEWHERE
       in the query, in any order/position. This catches real pilgrim
       phrasing like "keep MY luggage" or "where I can store luggage",
       which wouldn't contain "keep luggage" as an exact substring but
       clearly means the same thing.
    """
    ql = query.lower()
    query_words = _word_set(query)
    matched = set()

    for phrase, concept in _ALL_SYNONYM_PHRASES:
        if concept in matched:
            continue
        if phrase in ql:
            matched.add(concept)
            continue
        phrase_words = _word_set(phrase)
        if len(phrase_words) >= 2 and phrase_words.issubset(query_words):
            matched.add(concept)

    return matched


def expand_query_words(query: str) -> set:
    """The query's own words PLUS every English/Telugu keyword belonging to
    any concept detected in the query. This expanded set is what we match
    against Q&A text, so recall is much higher than plain word overlap."""
    words = set(_word_set(query))
    for concept in expand_query_concepts(query):
        for lang_list in KEYWORD_SYNONYMS[concept].values():
            for phrase in lang_list:
                words |= _word_set(phrase)
    return words


def search_relevant_qas(query: str, top_n: int = 6):
    """Return the top_n (category_key, question, answer) tuples most
    relevant to a free-text query, using keyword + concept overlap.
    Questions matter more than answers, so a match in the question is
    weighted higher."""
    query_words = expand_query_words(query)
    if not query_words:
        return _QA_INDEX[:top_n]

    scored = []
    for key, q, a in _QA_INDEX:
        score = 2 * len(query_words & _word_set(q)) + len(query_words & _word_set(a))
        if score > 0:
            scored.append((score, key, q, a))

    if not scored:
        # No keyword overlap at all — fall back to a small general set so
        # the AI still has *some* grounding rather than none.
        return _QA_INDEX[:top_n]

    scored.sort(key=lambda item: item[0], reverse=True)
    return [(key, q, a) for _, key, q, a in scored[:top_n]]


def get_relevant_knowledge_text(query: str, top_n: int = 6) -> str:
    """Build a SHORT knowledge snippet — only the Q&As relevant to this one
    question — to use as grounding context for a single Groq request."""
    matches = search_relevant_qas(query, top_n=top_n)
    lines = []
    for key, q, a in matches:
        title = KNOWLEDGE_BASE[key]["title"]
        lines.append(f"[{title}]\nQ: {q}\nA: {a}")
    return "\n\n".join(lines)


# ------------------------------------------------------------------
# DIRECT ANSWER (zero Groq API calls) — the main cost-saving feature.
#
# If the expanded query overlaps a large enough FRACTION of a specific
# Q&A's own question words, we're confident enough to answer straight
# from the knowledge base — no AI call needed at all. Only questions
# that DON'T confidently match anything fall through to Groq.
# ------------------------------------------------------------------

DIRECT_MATCH_MIN_CONFIDENCE = 0.55  # >=55% of the matched question's words
DIRECT_MATCH_MIN_OVERLAP = 2        # normally need >=2 real words in common
DIRECT_MATCH_SINGLE_WORD_CONFIDENCE = 0.9  # ...unless it's a near-exact,
                                            # very short/specific question


def find_best_direct_match(query: str):
    """Try to find one clearly-best Q&A for this query.
    Returns (category_key, question, answer) if confident, else None.

    A match counts as confident if EITHER:
      (a) it shares >=2 real words with the query AND covers >=55% of the
          question's own words, OR
      (b) the question is very short/specific (<=2 real words after
          stopwords) and the query covers >=90% of it — e.g. a question
          that reduces to just {"laddu"} still deserves a direct answer
          when the pilgrim's message is clearly about laddus.
    """
    expanded = expand_query_words(query)
    if not expanded:
        return None

    best = None
    best_score = 0
    best_confidence = 0.0

    for key, q, a in _QA_INDEX:
        q_words = _word_set(q)
        if not q_words:
            continue
        overlap = expanded & q_words
        score = len(overlap)
        confidence = score / len(q_words)

        confident = (
            (score >= DIRECT_MATCH_MIN_OVERLAP and confidence >= DIRECT_MATCH_MIN_CONFIDENCE)
            or (score >= 1 and len(q_words) <= 2 and confidence >= DIRECT_MATCH_SINGLE_WORD_CONFIDENCE)
        )
        if not confident:
            continue

        # Prefer higher absolute overlap first, then higher confidence.
        if score > best_score or (score == best_score and confidence > best_confidence):
            best_score = score
            best_confidence = confidence
            best = (key, q, a)

    return best


def format_direct_answer(match, telugu: bool = False) -> str:
    """Format a directly-matched Q&A as a WhatsApp-friendly reply.
    Used when find_best_direct_match() is confident — this path costs
    NOTHING (no Groq API call)."""
    key, q, a = match
    title = KNOWLEDGE_BASE[key]["title"]
    if telugu:
        footer = "\n\n💬 మరింత సమాచారం కావాలంటే, మీ ప్రశ్నను తెలుగులో లేదా ఇంగ్లీష్‌లో అడగండి!"
    else:
        footer = "\n\n💬 Ask me anything else, in English or Telugu!"
    return f"*{title}*\n\n❓ {q}\n➡️ {a}{footer}"
