import logging
from .chroma_client import ChromaClient

logger = logging.getLogger(__name__)

JAPAN_DOCS = [
    {
        "id": "japan-overview",
        "destination": "japan",
        "category": "overview",
        "title": "Japan Travel Overview",
        "content": """Japan is an island nation in East Asia known for its unique blend of ancient traditions and cutting-edge modernity. The country offers diverse experiences from bustling cities like Tokyo and Osaka to serene temples in Kyoto and natural beauty in Hokkaido. Best times to visit are spring (March-May) for cherry blossoms and autumn (September-November) for fall foliage. Japan uses the Yen (JPY) and is known for being safe, clean, and efficient."""
    },
    {
        "id": "japan-tokyo",
        "destination": "japan",
        "category": "cities",
        "title": "Tokyo Guide",
        "content": """Tokyo is Japan's capital and largest city, a metropolis mixing ultramodern and traditional. Key areas include Shibuya (famous crossing, shopping), Shinjuku (nightlife, Kabukicho), Asakusa (historic Senso-ji Temple), Akihabara (electronics, anime culture), and Harajuku (youth fashion, Meiji Shrine). Must-see attractions: Tokyo Skytree, Imperial Palace, Tsukiji Outer Market, teamLab digital art museums. The city has an extensive subway and JR train network."""
    },
    {
        "id": "japan-kyoto",
        "destination": "japan",
        "category": "cities",
        "title": "Kyoto Guide",
        "content": """Kyoto was Japan's imperial capital for over 1000 years and remains the cultural heart of Japan with 17 UNESCO World Heritage sites. Must-visit: Fushimi Inari Shrine (thousands of orange torii gates), Kinkaku-ji (Golden Pavilion), Arashiyama Bamboo Grove, Gion district (geisha culture), Nijo Castle. The city has over 2000 temples and shrines. Best explored by bus or bicycle. Traditional ryokan stays and kaiseki cuisine are quintessential Kyoto experiences."""
    },
    {
        "id": "japan-osaka",
        "destination": "japan",
        "category": "cities",
        "title": "Osaka Guide",
        "content": """Osaka is Japan's kitchen, famous for street food culture. Must-try dishes: takoyaki (octopus balls), okonomiyaki (savory pancake), kushikatsu (deep-fried skewers). Key areas: Dotonbori (neon lights, Glico Man sign, food street), Shinsekai (retro district), Osaka Castle. The city is known for friendly locals and more relaxed atmosphere than Tokyo. Universal Studios Japan is a major attraction. Osaka is a great base for day trips to Nara, Kobe, and Himeji Castle."""
    },
    {
        "id": "japan-food",
        "destination": "japan",
        "category": "food",
        "title": "Japanese Cuisine Guide",
        "content": """Japanese cuisine is renowned worldwide. Essential experiences: sushi and sashimi (fresh raw fish), ramen (regional varieties include Tokyo shoyu, Hakata tonkotsu, Sapporo miso), tempura, yakitori (grilled chicken skewers), udon and soba noodles, wagyu beef, kaiseki (multi-course haute cuisine). Convenience stores (7-Eleven, Lawson, FamilyMart) offer surprisingly high-quality food. Izakayas are casual pubs perfect for sampling many dishes. Tipping is not practiced in Japan."""
    },
    {
        "id": "japan-transport",
        "destination": "japan",
        "category": "transport",
        "title": "Getting Around Japan",
        "content": """The Japan Rail Pass (JR Pass) offers unlimited travel on JR trains including most shinkansen (bullet trains) for 7, 14, or 21 days - must be purchased before arriving in Japan. Shinkansen connects major cities: Tokyo-Kyoto in 2h15m, Tokyo-Osaka in 2h30m. IC cards (Suica, Pasmo) work on all urban transit. Trains are punctual to the second. Last trains typically run around midnight. Domestic flights are efficient for reaching Okinawa or Hokkaido."""
    },
    {
        "id": "japan-culture",
        "destination": "japan",
        "category": "culture",
        "title": "Japanese Culture & Etiquette",
        "content": """Key etiquette: remove shoes when entering homes and many traditional establishments, bow as greeting, don't tip, be quiet on trains, don't eat while walking. Onsen (hot spring baths) require washing before entering and have tattoo restrictions at some locations. Many restaurants have plastic food displays outside. Cash is still widely used despite increasing card acceptance. Basic Japanese phrases appreciated: arigatou (thank you), sumimasen (excuse me), konnichiwa (hello)."""
    },
    {
        "id": "japan-seasons",
        "destination": "japan",
        "category": "seasons",
        "title": "Best Times to Visit Japan",
        "content": """Spring (March-May): Cherry blossom season peaks late March to early April, mild weather, Golden Week holiday (late April-early May) is extremely crowded. Summer (June-August): Hot and humid, rainy season in June, mountain hiking season, summer festivals. Autumn (September-November): Beautiful fall colors peak in November, comfortable temperatures, less crowded than spring. Winter (December-February): Cold but excellent for skiing in Niseko/Nagano, fewer tourists, illuminations in cities."""
    },
    {
        "id": "japan-mt-fuji",
        "destination": "japan",
        "category": "attractions",
        "title": "Mount Fuji Guide",
        "content": """Mount Fuji (3,776m) is Japan's highest peak and most iconic symbol. Best views: Hakone (also has hot springs), Kawaguchiko (Five Lakes region), Chureito Pagoda. Climbing season is July-August only. Day trips from Tokyo: take the Romance Car to Hakone or bus to Kawaguchiko. The mountain is visible from Tokyo on clear days but best viewed early morning. Lake Kawaguchiko offers boat rides with Fuji backdrop."""
    },
    {
        "id": "japan-nara",
        "destination": "japan",
        "category": "cities",
        "title": "Nara Day Trip",
        "content": """Nara, Japan's first permanent capital, is famous for over 1000 freely roaming sacred deer in Nara Park. Key sites: Todai-ji Temple housing a 15m bronze Buddha (one of world's largest wooden buildings), Kasuga Taisha shrine with thousands of lanterns, Isuien Garden. Easy day trip from Osaka (45 min) or Kyoto (1 hour). Deer crackers (shika senbei) available to feed the bowing deer. The deer are protected as national treasures."""
    },
]


def load_destination_documents(chroma_client: ChromaClient):
    """Load all destination documents into ChromaDB."""
    logger.info("Loading destination documents into ChromaDB...")
    chroma_client.add_destination_docs(JAPAN_DOCS)
    logger.info("Destination documents loaded successfully")


def init_destinations():
    """Initialize destinations collection with documents."""
    client = ChromaClient()
    load_destination_documents(client)
