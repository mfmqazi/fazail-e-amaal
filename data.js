const deeds = [
    {
        id: 1,
        title: "Good Intention",
        category: "spiritual",
        description: "The validity and reward of any good deed are intrinsically linked to the purity of one's intention. A good deed will only be rewarded if it is performed with the right intention. For instance, performing prayer solely for the pleasure of Allah will earn reward, but if done to impress others, it leads to sin. Even permissible daily activities like earning a livelihood, choosing a profession, or dressing well can be transformed into acts of worship when coupled with a good intention."
    },
    {
        id: 2,
        title: "Du'a (Supplication)",
        category: "worship",
        description: "The essence of worship. Asking from Allah connects the servant to the Creator and acknowledges one's dependence on Him."
    },
    {
        id: 3,
        title: "Prophetic Du'as",
        category: "worship",
        description: "Reciting the specific supplications taught by the Prophet ﷺ for various occasions brings barakah and follows the Sunnah."
    },
    {
        id: 4,
        title: "Seeking Forgiveness (Istighfar)",
        category: "spiritual",
        description: "Constantly seeking forgiveness cleanses the heart, removes sins, and opens the doors of sustenance and mercy."
    },
    {
        id: 5,
        title: "Dhikr (Remembrance) of Allah",
        category: "worship",
        description: "Keeping the tongue moist with the remembrance of Allah brings tranquility to the heart and immense rewards."
    },
    {
        id: 6,
        title: "Blessings upon the Prophet (Salawat)",
        category: "worship",
        description: "Sending blessings upon the Prophet ﷺ is a means of having one's own sins forgiven and concerns alleviated."
    },
    {
        id: 7,
        title: "Gratitude (Shukr)",
        category: "spiritual",
        description: "Expressing gratitude to Allah for His countless blessings ensures their increase and pleases the Lord."
    },
    {
        id: 8,
        title: "Patience (Sabr)",
        category: "character",
        description: "Enduring hardships with patience and trust in Allah's wisdom is a quality of the steadfast and brings immeasurable reward."
    },
    {
        id: 9,
        title: "Beginning with Bismillah",
        category: "daily",
        description: "Starting every important action with the name of Allah brings blessings and protection to that action."
    },
    {
        id: 10,
        title: "Initiating Salam",
        category: "social",
        description: "To precede in greeting is a Sunnah. Being the first to offer salam spreads peace and love. However, it is advisable to wait if the person is occupied with worship or study. If a group is seated, they should be greeted. Failing to reply to a salam is considered sinful. When a letter containing 'salam alaikum' is received, it should be responded to verbally."
    },
    {
        id: 11,
        title: "Visiting the Sick",
        category: "social",
        description: "Visiting the sick is an act of great merit and a right of a Muslim. The Prophet ﷺ said, 'When a Muslim visits his sick brother in faith, he is all the time in the garden of Paradise.' Another Hadith states that seventy thousand angels pray for the visitor's forgiveness. The proper etiquette includes placing one's hand on the sick person's forehead to offer comfort."
    },
    {
        id: 12,
        title: "Attending Funeral (Janazah)",
        category: "social",
        description: "Participating in the funeral prayer and burial of a Muslim fulfills a communal obligation and reminds one of the Hereafter."
    },
    {
        id: 13,
        title: "Consoling the Bereaved",
        category: "social",
        description: "Comforting those who have lost loved ones brings great reward and strengthens community bonds."
    },
    {
        id: 14,
        title: "Love for the Sake of Allah",
        category: "social",
        description: "Loving others not for worldly gain but solely for Allah's sake is a sign of true faith and leads to Allah's shade on Judgment Day."
    },
    {
        id: 15,
        title: "Helping a Muslim",
        category: "social",
        description: "Assisting a fellow Muslim in their time of need causes Allah to assist you in your time of need."
    },
    {
        id: 16,
        title: "Interceding for Good",
        category: "social",
        description: "Using one's influence to help someone in a permissible matter is a form of charity."
    },
    {
        id: 17,
        title: "Concealing Faults",
        category: "social",
        description: "Hiding the shortcomings of others leads to Allah concealing one's own faults in this world and the Hereafter."
    },
    {
        id: 18,
        title: "Guiding towards Good",
        category: "social",
        description: "Directing someone to a good deed earns the same reward as the doer of that deed."
    },
    {
        id: 19,
        title: "Charity (Sadaqah)",
        category: "charity",
        description: "Giving from one's wealth to those in need extinguishes sins like water extinguishes fire."
    },
    {
        id: 20,
        title: "Forgiving Others",
        category: "character",
        description: "Pardoning those who have wronged you is a noble trait that brings honor and Allah's forgiveness."
    },
    {
        id: 21,
        title: "Being Soft-Spoken",
        category: "character",
        description: "Speaking gently and kindly is a charity and reflects the beautiful character of a believer."
    },
    {
        id: 22,
        title: "Reconciliation",
        category: "social",
        description: "Making peace between two disputing parties is a highly virtuous act that preserves the unity of the community."
    },
    {
        id: 23,
        title: "Supporting Orphans & Widows",
        category: "charity",
        description: "Caring for the most vulnerable in society places one close to the Prophet ﷺ in Paradise."
    },
    {
        id: 24,
        title: "Spending on Family",
        category: "family",
        description: "Spending on one's own family with the intention of reward is considered a form of charity."
    },
    {
        id: 25,
        title: "Good Conduct with Parents",
        category: "family",
        description: "Treating parents with kindness, respect, and obedience is one of the greatest deeds after worshipping Allah."
    },
    {
        id: 26,
        title: "Respecting Parents' Friends",
        category: "family",
        description: "Maintaining ties with the friends and relatives of one's parents after they pass away is a form of dutifulness."
    },
    {
        id: 27,
        title: "Good Marital Relations",
        category: "family",
        description: "Treating one's spouse with love, mercy, and fairness is a sign of the best of believers."
    },
    {
        id: 28,
        title: "Maintaining Kinship Ties",
        category: "family",
        description: "Upholding ties with relatives extends one's life and increases provision."
    },
    {
        id: 29,
        title: "Good Treatment of Neighbors",
        category: "social",
        description: "Being kind and helpful to neighbors is a fundamental instruction of Jibreel (AS) to the Prophet ﷺ."
    },
    {
        id: 30,
        title: "Being Cheerful",
        category: "character",
        description: "Meeting others with a smiling face is a charity and brings joy to the hearts of believers."
    },
    {
        id: 31,
        title: "Good Travel Companionship",
        category: "social",
        description: "Being a helpful and considerate companion during travel is a sign of good character."
    },
    {
        id: 32,
        title: "Meeting for Allah's Sake",
        category: "social",
        description: "Visiting one another solely for the love of Allah strengthens the bond of brotherhood."
    },
    {
        id: 33,
        title: "Honoring Guests",
        category: "social",
        description: "Treating guests with generosity and respect is a sign of belief in Allah and the Last Day."
    },
    {
        id: 34,
        title: "Removing Obstacles",
        category: "social",
        description: "Removing harmful objects from the path is a branch of faith and a form of charity."
    },
    {
        id: 35,
        title: "Refraining from Arguments",
        category: "character",
        description: "Avoiding arguments, even when one is right, guarantees a house in the surroundings of Paradise."
    },
    {
        id: 36,
        title: "Learning Religion",
        category: "spiritual",
        description: "Seeking knowledge of Islam is an obligation and a path to Paradise."
    },
    {
        id: 37,
        title: "Teaching Religion",
        category: "spiritual",
        description: "Imparting beneficial knowledge is a continuous charity (Sadaqah Jariyah) that benefits one even after death."
    },
    {
        id: 38,
        title: "Respecting Elders",
        category: "social",
        description: "Showing honor to the elderly is part of glorifying Allah."
    },
    {
        id: 39,
        title: "Respecting Signs of Islam",
        category: "spiritual",
        description: "Venerating the symbols of Allah (like the Quran, Mosques) comes from the piety of the heart."
    },
    {
        id: 40,
        title: "Kindness to Children",
        category: "social",
        description: "Showing mercy and affection to children is a characteristic of the Prophet ﷺ."
    },
    {
        id: 41,
        title: "Performing Adhan",
        category: "worship",
        description: "Calling people to prayer earns the Mu'adhin forgiveness as far as his voice reaches."
    },
    {
        id: 42,
        title: "Responding to Adhan",
        category: "worship",
        description: "Repeating the words of the Adhan and reciting the dua afterwards guarantees the Prophet's intercession."
    },
    {
        id: 43,
        title: "Reciting Quran",
        category: "quran",
        description: "Reciting the Book of Allah brings ten rewards for every letter and intercedes for the reciter on Judgment Day."
    },
    {
        id: 44,
        title: "Reciting Surah Fatihah & Ikhlas",
        category: "quran",
        description: "Frequent recitation of these Surahs carries immense weight and reward."
    },
    {
        id: 45,
        title: "Perfecting Wudu",
        category: "worship",
        description: "Performing ablution thoroughly, especially in difficulty, washes away sins."
    },
    {
        id: 46,
        title: "Using Miswak",
        category: "daily",
        description: "Using the toothstick is a purification for the mouth and pleasing to the Lord."
    },
    {
        id: 47,
        title: "Dhikr after Wudu",
        category: "worship",
        description: "Reciting the testimony of faith after Wudu opens the eight gates of Paradise."
    },
    {
        id: 48,
        title: "Tahiyyat al-Wudu",
        category: "worship",
        description: "Praying two rak'ats after Wudu is a means of entering Paradise."
    },
    {
        id: 49,
        title: "Tahiyyat al-Masjid",
        category: "worship",
        description: "Praying two rak'ats upon entering the mosque honors the House of Allah."
    },
    {
        id: 50,
        title: "Intention of I'tikaf",
        category: "worship",
        description: "Making intention for I'tikaf whenever entering a mosque turns the visit into a period of worship."
    },
    {
        id: 51,
        title: "Praying in First Row",
        category: "worship",
        description: "The first row in prayer has the greatest reward, similar to the row of angels."
    },
    {
        id: 52,
        title: "Filling Gaps in Rows",
        category: "worship",
        description: "Connecting the rows in prayer connects one to Allah's mercy."
    },
    {
        id: 53,
        title: "Ishraq Prayer",
        category: "worship",
        description: "Praying after sunrise brings the reward of a complete Hajj and Umrah."
    },
    {
        id: 54,
        title: "Friday Preparations",
        category: "worship",
        description: "Bathing, using perfume, and wearing clean clothes on Friday are emphasized Sunnahs."
    },
    {
        id: 55,
        title: "Suhoor Meal",
        category: "worship",
        description: "Eating the pre-dawn meal before fasting is a blessed act."
    },
    {
        id: 56,
        title: "Hurrying Iftar",
        category: "worship",
        description: "Breaking the fast immediately after sunset is a beloved practice."
    },
    {
        id: 57,
        title: "Feeding a Fasting Person",
        category: "charity",
        description: "Providing Iftar for someone earns the same reward as their fast without diminishing their reward."
    },
    {
        id: 58,
        title: "Helping Families of Mujahids/Hajis",
        category: "social",
        description: "Taking care of the families of those striving in Allah's path shares in their reward."
    },
    {
        id: 59,
        title: "Praying for Martyrdom",
        category: "spiritual",
        description: "Sincerely asking Allah for martyrdom grants the rank of a martyr even if one dies in bed."
    },
    {
        id: 60,
        title: "Early Morning Work",
        category: "business",
        description: "Starting work early in the day brings barakah (blessing) as prayed for by the Prophet ﷺ."
    },
    {
        id: 61,
        title: "Dhikr in Marketplace",
        category: "business",
        description: "Remembering Allah in the market, a place of heedlessness, brings millions of rewards."
    },
    {
        id: 62,
        title: "Accepting Returned Goods",
        category: "business",
        description: "Accepting a return from a remorseful buyer leads to Allah forgiving one's slips."
    },
    {
        id: 63,
        title: "Lending to Needy",
        category: "charity",
        description: "Giving a loan to someone in need is rewarded as half of charity."
    },
    {
        id: 64,
        title: "Leniency with Debtors",
        category: "charity",
        description: "Giving more time or forgiving a debt earns the shade of Allah's Throne."
    },
    {
        id: 65,
        title: "Truth in Trade",
        category: "business",
        description: "An honest merchant will be raised with the Prophets and Martyrs."
    },
    {
        id: 66,
        title: "Planting Trees",
        category: "charity",
        description: "Any benefit derived by humans or animals from a planted tree counts as charity."
    },
    {
        id: 67,
        title: "Kindness to Animals",
        category: "misc",
        description: "Showing mercy to animals can be a means of forgiveness for sins."
    },
    {
        id: 68,
        title: "Killing Harmful Animals",
        category: "misc",
        description: "Protecting people from harm by removing dangerous pests is a good deed."
    },
    {
        id: 69,
        title: "Controlling the Tongue",
        category: "character",
        description: "Restraining speech protects one from many sins and is a guarantee of Paradise."
    },
    {
        id: 70,
        title: "Avoiding Useless Activities",
        category: "character",
        description: "Leaving that which does not concern one is a sign of the perfection of one's Islam."
    },
    {
        id: 71,
        title: "Six Good Deeds",
        category: "character",
        description: "Truthfulness, fulfilling trusts, chastity, lowering gaze, restraining hands, and fulfilling promises."
    },
    {
        id: 72,
        title: "Starting from Right",
        category: "daily",
        description: "Using the right hand and starting from the right side in good things is the Sunnah."
    },
    {
        id: 73,
        title: "Cleaning Dropped Morsel",
        category: "daily",
        description: "Picking up, cleaning, and eating fallen food shows humility and appreciation for sustenance."
    },
    {
        id: 74,
        title: "Sneezing Etiquette",
        category: "daily",
        description: "Praising Allah when sneezing and responding to the one who sneezes is a mutual right."
    },
    {
        id: 75,
        title: "Fear of Allah (Taqwa)",
        category: "spiritual",
        description: "Consciousness of Allah in private and public is the root of all goodness."
    },
    {
        id: 76,
        title: "Optimism & Hope",
        category: "spiritual",
        description: "Having good expectations of Allah and hope in His mercy is an act of worship."
    },
    {
        id: 77,
        title: "Modesty (Haya)",
        category: "character",
        description: "Modesty is a branch of faith and brings nothing but good."
    },
    {
        id: 78,
        title: "Consultation (Istikhara)",
        category: "spiritual",
        description: "Seeking Allah's guidance in matters prevents regret."
    },
    {
        id: 79,
        title: "Consulting Others (Shura)",
        category: "social",
        description: "Seeking advice from wise people is a safety from mistakes."
    },
    {
        id: 80,
        title: "Visiting Graveyards",
        category: "spiritual",
        description: "Visiting graves reminds one of death and softens the heart."
    },
    {
        id: 81,
        title: "Making Wudu before Sleep",
        category: "daily",
        description: "Sleeping in a state of purity invites the prayers of angels."
    },
    {
        id: 82,
        title: "Forgiving Debt",
        category: "charity",
        description: "Forgiving a debt for a person in difficulty is a deed of high status."
    }
];
