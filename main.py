"""
DOOMSDAY RACE  v3
Pixel-art survival horror. One random killer per round.
NEW: pixel sprites, side panel controls, HP/hearts, NPC healing, stun mechanic
"""
import pygame, random, math, sys, asyncio
from collections import deque

# Layout
PANEL_W  = 190
SCREEN_W = 1024
SCREEN_H = 768
GAME_W   = SCREEN_W - PANEL_W   # 834 px gameplay area
HUD_H    = 42
TILE     = 32
COLS     = GAME_W  // TILE
ROWS     = (SCREEN_H - HUD_H) // TILE
FPS      = 60

# Colors
BLACK      = (0,   0,   0)
DARK_GRAY  = (14,  14,  20)
GRAY       = (55,  55,  65)
WALL_CLR   = (32,  32,  52)
WALL_TOP   = (52,  52,  78)
FLOOR_CLR  = (20,  20,  30)
RED        = (220, 50,  50)
DARK_RED   = (130, 15,  15)
GREEN      = (50,  200, 80)
DARK_GREEN = (20,  90,  40)
YELLOW     = (230, 200, 50)
ORANGE     = (230, 130, 30)
WHITE      = (240, 240, 240)
CYAN       = (50,  210, 225)
PURPLE     = (155, 50,  200)
PINK       = (220, 100, 180)
SKIN       = (230, 190, 140)
DARK_SKIN  = (180, 130,  90)
BROWN      = (100,  60,  20)
PANEL_BG   = (8,    8,  14)

WALL=0; FLOOR=1

STATE_MENU="menu"; STATE_REVEAL="reveal"
STATE_PLAYING="playing"; STATE_WIN="win"; STATE_LOSE="lose"

REVEAL_DUR   = 4.0
MAX_HP       = 3
STUN_CD      = 4.0
STUN_DUR     = 2.5
STUN_RANGE   = 2.2
HEAL_RANGE   = 2.0
HEAL_RATE    = 0.6
HIT_CD       = 1.5

# Gold rewards
GOLD_PER_GEN      = 50     # gold for each generator completed
GOLD_PER_ESCAPE   = 200    # gold when you escape
GOLD_PER_SURV_ESC = 25     # gold for each survivor that escapes
GOLD_PER_STUN     = 15     # gold each time you stun the killer
GOLD_COIN_COLOR   = (255, 215, 0)

# â”€â”€ Shop & Equipment â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
STATE_SHOP="shop"; STATE_CITY="city"
STATE_FINALE_REVEAL="finale_reveal"; STATE_FINALE="finale"; STATE_FINALE_WIN="finale_win"

SHOP_ITEMS = [
    {"id":"knight_helm","name":"Knight Helmet","slot":"helmet","cost":150,"color":(180,180,200),"desc":"+1 HP","bonus":{"max_hp":1}},
    {"id":"bright_helm","name":"Bright Helmet","slot":"helmet","cost":300,"color":(255,230,50),"desc":"+1 HP +stun","bonus":{"max_hp":1,"stun_range":0.5}},
    {"id":"shadow_hood","name":"Shadow Hood","slot":"helmet","cost":200,"color":(40,20,60),"desc":"+speed","bonus":{"speed":0.5}},
    {"id":"golden_crown","name":"Golden Crown","slot":"helmet","cost":500,"color":(255,215,0),"desc":"+2 HP","bonus":{"max_hp":2}},
    {"id":"chain_mail","name":"Chain Mail","slot":"armor","cost":200,"color":(150,150,160),"desc":"+1 HP","bonus":{"max_hp":1}},
    {"id":"plate_armor","name":"Plate Armor","slot":"armor","cost":400,"color":(100,120,180),"desc":"+2 HP slower","bonus":{"max_hp":2,"speed":-0.3}},
    {"id":"dark_cloak","name":"Dark Cloak","slot":"armor","cost":250,"color":(30,15,50),"desc":"+speed","bonus":{"speed":0.8}},
    {"id":"iron_sword","name":"Iron Sword","slot":"weapon","cost":150,"color":(200,200,210),"desc":"+stun range","bonus":{"stun_range":0.5}},
    {"id":"battle_axe","name":"Battle Axe","slot":"weapon","cost":300,"color":(180,100,50),"desc":"+stun time","bonus":{"stun_dur":1.0}},
    {"id":"magic_staff","name":"Magic Staff","slot":"weapon","cost":350,"color":(130,50,200),"desc":"faster stun","bonus":{"stun_cd":-1.0}},
]

BOSS_DEFS = [
    {"name":"Goblin Chief","hp":5,"speed":2.8,"damage":1,"color":(80,160,40),"gold":200,"tx":25,"ty":42},
    {"name":"Stone Troll","hp":8,"speed":1.5,"damage":2,"color":(120,100,80),"gold":350,"tx":55,"ty":42},
    {"name":"Shadow Dragon","hp":12,"speed":2.2,"damage":2,"color":(60,20,100),"gold":500,"tx":40,"ty":48},
    {"name":"Fire Imp","hp":4,"speed":3.5,"damage":1,"color":(220,80,20),"gold":150,"tx":30,"ty":50},
    {"name":"Ice Golem","hp":10,"speed":1.2,"damage":3,"color":(100,180,220),"gold":400,"tx":50,"ty":50},
    {"name":"Dark Knight","hp":9,"speed":2.5,"damage":2,"color":(30,30,40),"gold":450,"tx":35,"ty":45},
    {"name":"Bone Reaver","hp":7,"speed":2.8,"damage":2,"color":(200,190,150),"gold":300,"tx":45,"ty":45},
    {"name":"Venom Queen","hp":15,"speed":2.0,"damage":3,"color":(80,200,60),"gold":600,"tx":40,"ty":53},
]

CITY_W=80; CITY_H=60; GOLD_FINALE_WIN=10000
C_GRASS=10; C_PATH=11; C_BWALL=12; C_WATER=13; C_BFLOOR=14; C_BED=15
C_SAND=16; C_SNOW=17; C_LAVA=18; C_MUSHROOM=19; C_SWAMP=20; C_DARKGRASS=21
CITY_COLORS={
    C_GRASS:(40,85,35),C_PATH:(160,145,110),C_BWALL:(90,70,50),C_WATER:(40,80,170),
    C_BFLOOR:(120,100,70),C_BED:(90,40,40),C_SAND:(210,190,130),C_SNOW:(220,225,235),
    C_LAVA:(180,50,20),C_MUSHROOM:(70,40,80),C_SWAMP:(50,70,35),C_DARKGRASS:(25,55,20),
}
PORTAL_POS=(75,55)

# Quest system
QUESTS = [
    {"id":"talk_elder","name":"Meet the Elder","desc":"Talk to Elder Mara","gold":50,"type":"talk","target":"Elder Mara"},
    {"id":"talk_scout","name":"Scout's Intel","desc":"Talk to Scout Rex","gold":50,"type":"talk","target":"Scout Rex"},
    {"id":"buy_gear","name":"Gear Up!","desc":"Buy something from Blacksmith","gold":75,"type":"buy","target":"gear"},
    {"id":"buy_food","name":"Full Belly","desc":"Buy food from Baker Bob","gold":40,"type":"buy","target":"food"},
    {"id":"buy_potion","name":"Brew Master","desc":"Buy a potion from Witch Vera","gold":60,"type":"buy","target":"potion"},
    {"id":"visit_house","name":"Home Sweet Home","desc":"Visit your private house","gold":100,"type":"zone","target":"house"},
    {"id":"heal_up","name":"Patched Up","desc":"Get healed by Healer Luna","gold":30,"type":"talk","target":"Healer Luna"},
    {"id":"kill_goblin","name":"Goblin Slayer","desc":"Defeat the Goblin Chief","gold":100,"type":"kill","target":"Goblin Chief"},
    {"id":"kill_troll","name":"Troll Crusher","desc":"Defeat the Stone Troll","gold":150,"type":"kill","target":"Stone Troll"},
    {"id":"kill_dragon","name":"Dragon Bane","desc":"Defeat the Shadow Dragon","gold":200,"type":"kill","target":"Shadow Dragon"},
    {"id":"kill_imp","name":"Imp Hunter","desc":"Defeat the Fire Imp","gold":80,"type":"kill","target":"Fire Imp"},
    {"id":"kill_golem","name":"Golem Breaker","desc":"Defeat the Ice Golem","gold":180,"type":"kill","target":"Ice Golem"},
    {"id":"kill_knight","name":"Knight's End","desc":"Defeat the Dark Knight","gold":200,"type":"kill","target":"Dark Knight"},
    {"id":"kill_reaver","name":"Bone Collector","desc":"Defeat the Bone Reaver","gold":150,"type":"kill","target":"Bone Reaver"},
    {"id":"kill_queen","name":"Queen Slayer","desc":"Defeat the Venom Queen","gold":300,"type":"kill","target":"Venom Queen"},
    {"id":"kill_all","name":"Champion!","desc":"Defeat ALL bosses","gold":500,"type":"kill_all","target":None},
    {"id":"explore_desert","name":"Sand Walker","desc":"Walk on desert sand","gold":40,"type":"zone","target":"desert"},
    {"id":"explore_snow","name":"Frostbite","desc":"Walk through the snow","gold":40,"type":"zone","target":"snow"},
    {"id":"explore_mushroom","name":"Shroom Seeker","desc":"Explore mushroom forest","gold":40,"type":"zone","target":"mushroom"},
    {"id":"explore_swamp","name":"Swamp Thing","desc":"Explore the swamp","gold":40,"type":"zone","target":"swamp"},
    {"id":"chef_meal","name":"Fine Dining","desc":"Eat a meal from your Chef","gold":60,"type":"buy","target":"chef"},
]

# Consumable items you can buy from city shops
CONSUMABLES = [
    {"id":"bread","name":"Fresh Bread","cost":20,"desc":"Heals 1 HP","heal":1},
    {"id":"steak","name":"Grilled Steak","cost":50,"desc":"Heals 2 HP","heal":2},
    {"id":"feast","name":"Royal Feast","cost":120,"desc":"Full heal!","heal":99},
    {"id":"speed_pot","name":"Speed Potion","cost":80,"desc":"Speed boost next round","heal":0,"buff":"speed"},
    {"id":"shield_pot","name":"Shield Potion","cost":100,"desc":"+1 temp HP next round","heal":0,"buff":"shield"},
    {"id":"stun_pot","name":"Stun Potion","cost":90,"desc":"Stun CD -1s next round","heal":0,"buff":"stun"},
    {"id":"cookie","name":"Magic Cookie","cost":30,"desc":"Heals 1 HP + yummy!","heal":1},
    {"id":"pet_snack","name":"Pet Snack","cost":15,"desc":"Heals 0.5 HP","heal":0.5},
]

# Arrow signs placed on the city map
CITY_ARROWS = [
    # (tile_x, tile_y, direction, label)
    (40, 20, "up",    "Shops"),
    (40, 35, "down",  "Arena"),
    (33, 30, "left",  "West Side"),
    (47, 30, "right", "East Side"),
    (40, 10, "up",    "Blacksmith"),
    (55, 30, "right", "Healer"),
    (25, 30, "left",  "Scout"),
    (40, 44, "down",  "Bosses!"),
    (70, 50, "right", "Portal"),
    (15, 10, "left",  "Bakery"),
    (60, 10, "right", "Potions"),
    (15, 35, "down",  "Pet Shop"),
    (65, 35, "down",  "Library"),
    (40, 15, "up",    "Inn"),
    (58, 20, "right", "My House"),
]

CITY_NPC_DEFS = [
    {"name":"Elder Mara","tx":40,"ty":28,"color":(200,180,100),"dialog":["Welcome to Haven City!","You survived the dungeon...","Defeat the 3 bosses to unlock the portal.","The portal leads to the FINAL challenge!"],"heals":False,"is_shop":False,"shop_type":None},
    {"name":"Blacksmith","tx":22,"ty":8,"color":(180,80,40),"dialog":["Welcome to my shop!","Press ENTER to browse gear."],"heals":False,"is_shop":True,"shop_type":"gear"},
    {"name":"Healer Luna","tx":62,"ty":8,"color":(100,220,150),"dialog":["Let me heal your wounds...","Stay safe out there!"],"heals":True,"is_shop":False,"shop_type":None},
    {"name":"Scout Rex","tx":10,"ty":25,"color":(200,150,50),"dialog":["3 bosses guard the south arena.","Goblin Chief is the easiest.","Shadow Dragon is the hardest!","Defeat them all to open the portal."],"heals":False,"is_shop":False,"shop_type":None},
    {"name":"Baker Bob","tx":8,"ty":8,"color":(210,170,90),"dialog":["Welcome to the Bakery!","Fresh bread and cookies!","Press ENTER to buy food."],"heals":False,"is_shop":True,"shop_type":"food"},
    {"name":"Witch Vera","tx":63,"ty":8,"color":(140,60,200),"dialog":["Potions and elixirs!","Boost your speed or defense.","Press ENTER to browse."],"heals":False,"is_shop":True,"shop_type":"potion"},
    {"name":"Pet Keeper","tx":8,"ty":42,"color":(180,140,80),"dialog":["Welcome to the Pet Shop!","Pet snacks make you feel better!","Press ENTER to buy snacks."],"heals":False,"is_shop":True,"shop_type":"pet"},
    {"name":"Librarian","tx":63,"ty":22,"color":(100,100,180),"dialog":["Welcome to the Library!","Knowledge is power...","I sell magical scrolls.","Press ENTER to browse."],"heals":False,"is_shop":True,"shop_type":"scroll"},
    {"name":"Innkeeper","tx":40,"ty":12,"color":(160,120,80),"dialog":["Welcome to the Inn!","Rest here to heal fully.","A warm meal costs 40g."],"heals":False,"is_shop":True,"shop_type":"inn"},
    {"name":"Chef Pierre","tx":72,"ty":3,"color":(230,200,140),"dialog":["Welcome home, Master!","I've prepared your favorite meal.","Everything is free for you!","Press ENTER to choose!"],"heals":True,"is_shop":True,"shop_type":"chef","stay":True},
    {"name":"Butler James","tx":74,"ty":3,"color":(60,60,80),"dialog":["Good to see you, sir.","Your bed is freshly made.","This house is your safe haven.","No enemies can enter here.","Rest well before your next battle!"],"heals":True,"is_shop":False,"shop_type":None,"stay":True},
]


# â”€â”€ Map â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def generate_map():
    grid = [[WALL]*COLS for _ in range(ROWS)]
    rooms = []
    attempts = 0
    while len(rooms) < 9 and attempts < 300:
        attempts += 1
        w = random.randint(4, 9); h = random.randint(4, 7)
        x = random.randint(1, COLS-w-1); y = random.randint(1, ROWS-h-1)
        if any(x<rx+rw+1 and x+w+1>rx and y<ry+rh+1 and y+h+1>ry
               for rx,ry,rw,rh in rooms): continue
        for ry2 in range(y, y+h):
            for rx2 in range(x, x+w): grid[ry2][rx2] = FLOOR
        rooms.append((x,y,w,h))
    for i in range(len(rooms)-1):
        x1=rooms[i][0]+rooms[i][2]//2; y1=rooms[i][1]+rooms[i][3]//2
        x2=rooms[i+1][0]+rooms[i+1][2]//2; y2=rooms[i+1][1]+rooms[i+1][3]//2
        cx,cy=x1,y1
        while cx!=x2: grid[cy][cx]=FLOOR; cx+=1 if cx<x2 else -1
        while cy!=y2: grid[cy][cx]=FLOOR; cy+=1 if cy<y2 else -1
    return grid, rooms

def room_center(r): return (r[0]+r[2]//2, r[1]+r[3]//2)
def floor_tiles(grid): return [(c,r) for r in range(ROWS) for c in range(COLS) if grid[r][c]==FLOOR]

def bfs_path(grid, start, goal):
    if start==goal: return None
    q=deque([(start,[])]); vis={start}
    while q:
        (cx,cy),path=q.popleft()
        for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx,ny=cx+dx,cy+dy
            if 0<=nx<COLS and 0<=ny<ROWS and (nx,ny) not in vis and grid[ny][nx]==FLOOR:
                np2=path+[(nx,ny)]
                if (nx,ny)==goal: return np2[0] if np2 else None
                vis.add((nx,ny)); q.append(((nx,ny),np2))
    return None


# â”€â”€ Pixel-art drawing helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def px(surf, col, x, y, ox, oy, s=2):
    pygame.draw.rect(surf, col, (ox+x*s, oy+y*s, s, s))

def draw_player_sprite(surf, cx, cy, repairing=False, slowed=False, flash=False, stunned=False, equip=None):
    if equip is None: equip={}
    S=2; ox=cx-16; oy=cy-16
    def p(x,y,c): px(surf,c,x,y,ox,oy,S)
    armor_item=equip.get("armor")
    if armor_item and not flash:
        shirt=armor_item["color"]
    else:
        shirt = (80,80,200) if not slowed else (60,100,180)
    if flash: shirt=(220,60,60)
    hair=(35,20,10); sk=SKIN; boot=(45,35,70); belt=(90,65,30)
    # Head
    for r in range(1,5):
        for c in range(5,11): p(c,r,sk)
    for c in range(4,12): p(c,0,hair)
    for c in range(5,11): p(c,1,hair)
    p(4,3,DARK_SKIN); p(11,3,DARK_SKIN)
    p(6,3,(20,20,20)); p(9,3,(20,20,20))  # eyes
    p(7,4,(200,120,100))                   # mouth
    # Helmet overlay
    helm=equip.get("helmet")
    if helm:
        hc=helm["color"]; hd=tuple(max(0,c-40) for c in hc)
        for c in range(4,12): p(c,0,hc)
        for c in range(5,11): p(c,1,hc)
        p(4,1,hd); p(11,1,hd); p(4,2,hd); p(11,2,hd)
        if helm["id"]=="golden_crown":
            p(5,0,(255,180,0)); p(7,0,(255,180,0)); p(9,0,(255,180,0))
        elif helm["id"]=="bright_helm":
            for c2 in range(5,11): p(c2,0,(255,255,100))
            p(7,0,(255,255,200)); p(8,0,(255,255,200))
    # Body
    for r in range(5,10):
        for c in range(4,12): p(c,r,shirt)
    # Belt
    for c in range(4,12): p(c,9,belt)
    p(7,9,(60,45,20)); p(8,9,(60,45,20))  # buckle
    # Arms
    for r in range(5,10): p(3,r,sk); p(12,r,sk)
    # Hands
    p(3,9,sk); p(12,9,sk); p(3,10,sk); p(12,10,sk)
    # Weapon in right hand
    weap=equip.get("weapon")
    if weap and not repairing:
        wc=weap["color"]
        if "sword" in weap["id"]:
            for r2 in range(4,10): p(13,r2,wc)
            p(13,3,(160,160,170)); p(14,7,wc); p(14,8,wc)
        elif "axe" in weap["id"]:
            for r2 in range(4,10): p(13,r2,wc)
            p(14,4,wc); p(14,5,wc); p(15,5,wc); p(14,6,wc)
        elif "staff" in weap["id"]:
            for r2 in range(2,12): p(13,r2,wc)
            p(12,2,wc); p(14,2,wc); p(13,1,(200,150,255))
    # Legs
    leg=(max(0,shirt[0]-40),max(0,shirt[1]-40),max(0,shirt[2]-40))
    for r in range(10,14):
        for c in range(4,8): p(c,r,leg)
        for c in range(8,12): p(c,r,leg)
        p(7,r,(max(0,leg[0]-15),max(0,leg[1]-15),max(0,leg[2]-15)))
        p(8,r,(max(0,leg[0]-15),max(0,leg[1]-15),max(0,leg[2]-15)))
    # Boots
    for c in range(3,8): p(c,14,boot); p(c,15,boot)
    for c in range(8,13): p(c,14,boot); p(c,15,boot)
    p(3,14,boot); p(12,14,boot)
    # Wrench if repairing
    if repairing:
        for r in range(6,12): p(13,r,YELLOW); p(14,r,YELLOW)
        p(13,5,YELLOW); p(15,8,YELLOW); p(15,9,YELLOW)
    # Stun stars if stunned
    if stunned:
        t=pygame.time.get_ticks()/400.0
        for i in range(4):
            a=t+i*math.pi/2
            sx2=cx+int(math.cos(a)*14); sy2=cy-20+int(math.sin(a)*5)
            pygame.draw.circle(surf,YELLOW,(sx2,sy2),3)

def draw_survivor_sprite(surf, cx, cy, color, initial, frame=0, healing=False):
    S=2; ox=cx-16; oy=cy-16
    def p(x,y,c): px(surf,c,x,y,ox,oy,S)
    hair_map={'M':(170,90,50),'J':(20,15,8),'A':(200,170,40),'O':(70,45,15)}
    hair=hair_map.get(initial,(80,55,25))
    shirt=color; dark_s=tuple(max(0,c-60) for c in color); sk=SKIN
    pant=tuple(max(0,c-80) for c in color)
    boot=(40,35,65)
    # Head
    for r in range(1,5):
        for c in range(5,11): p(c,r,sk)
    for c in range(4,12): p(c,0,hair)
    for c in range(5,11): p(c,1,hair)
    p(4,3,DARK_SKIN); p(11,3,DARK_SKIN)
    blink=(frame//30)%8!=0
    if blink: p(6,3,(25,25,25)); p(9,3,(25,25,25))
    p(7,4,(195,115,95))
    # Body
    for r in range(5,10):
        for c in range(4,12): p(c,r,shirt)
    p(7,5,dark_s); p(8,5,dark_s)
    for r in range(5,9): p(3,r,sk); p(12,r,sk)
    p(3,9,sk); p(12,9,sk)
    # Legs
    for r in range(10,14):
        for c in range(4,12): p(c,r,pant)
    for c in range(3,8): p(c,14,boot); p(c,15,boot)
    for c in range(8,13): p(c,14,boot); p(c,15,boot)
    # Healing glow
    if healing:
        t=pygame.time.get_ticks()/300.0
        r2=int(20+4*math.sin(t))
        s2=pygame.Surface((r2*2,r2*2),pygame.SRCALPHA)
        pygame.draw.circle(s2,(80,255,120,60),(r2,r2),r2)
        surf.blit(s2,(cx-r2,cy-r2))
        pygame.draw.circle(surf,GREEN,(cx,cy-20),4)

def draw_killer_sprite(surf, cx, cy, ktype, stunned=False, frame=0):
    S=2; ox=cx-16; oy=cy-16
    def p(x,y,c): px(surf,c,x,y,ox,oy,S)

    if stunned:
        for r in range(16):
            for c in range(16): p(c,r,(45,45,45))
        t=frame*0.05
        for i in range(4):
            a=t*2+i*math.pi/2
            sx2=cx+int(math.cos(a)*16); sy2=cy-20+int(math.sin(a)*6)
            pygame.draw.circle(surf,YELLOW,(sx2,sy2),3)
        return

    if ktype=="WRAITH":
        cape=(150,15,15); hood=(100,5,5); eyes=(255,70,30); claw=(200,30,30)
        for r in range(3,16):
            for c in range(3,13): p(c,r,cape)
        for r in range(3,16): p(2,r,hood); p(13,r,hood)
        for r in range(0,4):
            for c in range(4,12): p(c,r,hood)
        # Horns
        p(4,0,(210,25,25)); p(3,1,(210,25,25)); p(3,0,(180,10,10))
        p(11,0,(210,25,25)); p(12,1,(210,25,25)); p(12,0,(180,10,10))
        # Eyes
        p(6,4,eyes); p(7,4,eyes); p(9,4,eyes); p(10,4,eyes)
        # Sneer
        p(7,6,(80,5,5)); p(8,6,(80,5,5)); p(9,6,(80,5,5))
        # Claws
        p(1,10,claw); p(2,11,claw); p(1,12,claw)
        p(14,10,claw); p(13,11,claw); p(14,12,claw)
        # Robe tatter
        for c in [3,5,7,9,11]: p(c,15,hood)

    elif ktype=="PHANTOM":
        ghost=(50,70,190); glow=(120,150,255); dark=(15,25,90); trans=(35,50,155)
        for r in range(2,13):
            for c in range(4,12): p(c,r,ghost)
        for r in range(2,10): p(3,r,trans); p(12,r,trans)
        for r in range(0,4):
            for c in range(5,11): p(c,r,glow)
        # Hollow eyes
        p(6,2,dark); p(7,2,dark); p(9,2,dark); p(10,2,dark)
        # Wail mouth
        for c in range(7,10): p(c,4,dark)
        # Ghost tail ripple
        for c in range(4,12,2): p(c,13,trans); p(c+1,14,trans); p(c,15,dark)
        # Reach
        p(2,7,glow); p(1,8,glow); p(1,9,glow)
        p(13,7,glow); p(14,8,glow); p(14,9,glow)

    elif ktype=="STALKER":
        body=(12,12,15); eyes=(0,255,110); cloak=(8,8,10)
        for r in range(1,15):
            for c in range(4,12): p(c,r,body)
        for r in range(3,13): p(3,r,cloak); p(12,r,cloak)
        for r in range(0,4):
            for c in range(5,11): p(c,r,body)
        p(5,2,eyes); p(6,2,eyes); p(9,2,eyes); p(10,2,eyes)
        p(7,4,(0,180,70)); p(8,4,(0,180,70))  # mouth slit
        p(2,9,eyes); p(1,10,eyes); p(1,11,eyes)
        p(13,9,eyes); p(14,10,eyes); p(14,11,eyes)
        for c in [4,6,8,10]: p(c,15,cloak)

    elif ktype=="BLIGHT":
        body=(65,0,95); energy=(195,45,255); dark=(25,0,45); crack=(255,145,255)
        for r in range(2,14):
            for c in range(4,12): p(c,r,body)
        for r in range(0,4):
            for c in range(5,11): p(c,r,energy)
        p(6,1,dark); p(7,1,dark); p(9,1,dark); p(10,1,dark)
        p(7,3,crack); p(8,3,crack)
        # Energy cracks
        p(5,5,crack); p(9,7,crack); p(6,10,crack); p(10,9,crack); p(7,12,crack)
        # Tendrils
        p(3,6,energy); p(2,7,energy); p(1,8,energy); p(1,9,energy)
        p(12,6,energy); p(13,7,energy); p(14,8,energy); p(14,9,energy)
        for c in range(4,12): p(c,14,dark); p(c,15,energy if c%2==0 else dark)

    elif ktype=="REAPER":
        robe=(8,8,8); shroud=(18,16,10); eyes=(255,200,0); bone=(215,205,175); gold=(175,145,0)
        for r in range(2,16):
            for c in range(3,13): p(c,r,robe)
        for r in range(2,14): p(2,r,shroud); p(13,r,shroud)
        for r in range(0,4):
            for c in range(5,11): p(c,r,bone)
        # Skull details
        p(6,1,robe); p(7,1,robe); p(9,1,robe); p(10,1,robe)
        p(6,2,eyes); p(10,2,eyes)
        p(6,3,robe); p(8,3,robe); p(10,3,robe)
        # Scythe
        for r in range(3,13): p(14,r,gold); p(15,r,gold)
        for c in range(9,16): p(c,3,bone)
        for c in range(10,15): p(c,4,bone)
        p(14,5,bone); p(13,9,bone); p(13,10,bone)
        for c in [3,5,7,9,11]: p(c,15,shroud)


# â”€â”€ Generator â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class Generator:
    def __init__(self,tx,ty):
        self.tx=tx; self.ty=ty; self.progress=0.0; self.active=False; self.done=False
    def update(self,dt):
        if self.active and not self.done:
            self.progress+=dt*(1.0/5.0)
            if self.progress>=1.0: self.progress=1.0; self.done=True
        elif not self.active and self.progress>0 and not self.done:
            self.progress=max(0,self.progress-dt*0.03)
    def draw(self,surf):
        px2=self.tx*TILE+TILE//2; py2=self.ty*TILE+TILE//2+HUD_H
        col=GREEN if self.done else (YELLOW if self.active else ORANGE)
        pygame.draw.rect(surf,(35,35,35),(px2-13,py2-13,26,24))
        pygame.draw.rect(surf,(65,65,65),(px2-13,py2-13,26,24),1)
        pygame.draw.rect(surf,GRAY,(px2-11,py2-11,4,4))
        pygame.draw.rect(surf,GRAY,(px2+7, py2-11,4,4))
        pygame.draw.rect(surf,col, (px2-5, py2-7, 10,10))
        pygame.draw.rect(surf,WHITE,(px2-5, py2-7, 10,10),1)
        for i in range(3): pygame.draw.rect(surf,BLACK,(px2-8+i*6,py2+4,4,3))
        if not self.done:
            pygame.draw.rect(surf,(25,25,25),(px2-13,py2+10,26,5))
            pygame.draw.rect(surf,GREEN,    (px2-13,py2+10,int(26*self.progress),5))
            pygame.draw.rect(surf,GRAY,     (px2-13,py2+10,26,5),1)
            if self.active and self.progress<1.0:
                secs=(1.0-self.progress)*5.0
                eta=pygame.font.SysFont("consolas",10).render(f"{secs:.1f}s",True,YELLOW)
                surf.blit(eta,(px2-eta.get_width()//2,py2+17))


# â”€â”€ Survivor NPC â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class Survivor:
    def __init__(self,tx,ty,name,color):
        self.tx=float(tx); self.ty=float(ty)
        self.name=name; self.color=color
        self.speed=random.uniform(1.8,2.5)
        self.alive=True; self.escaped=False
        self.target=None; self.path_timer=0.0
        self.repairing=False; self.assigned_gen=None
        self.healing=False; self.frame=random.randint(0,200)
        self.respawn_timer=0.0
        self.spawn_tx=float(tx); self.spawn_ty=float(ty)
    @property
    def tile(self): return (int(round(self.tx)),int(round(self.ty)))

    def update(self,dt,grid,generators,exit_open,exit_pos,killer_tiles,player):
        # Respawn countdown when dead
        if not self.alive:
            self.respawn_timer-=dt
            if self.respawn_timer<=0:
                self.alive=True; self.escaped=False
                self.target=None; self.path_timer=0.0
                self.assigned_gen=None
                # Respawn at original spawn point (safe corner of map)
                self.tx=self.spawn_tx; self.ty=self.spawn_ty
            return
        if self.escaped: return
        self.frame+=1; self.path_timer-=dt; self.healing=False; self.repairing=False
        min_k=min(math.dist((self.tx,self.ty),kt) for kt in killer_tiles)
        fleeing=min_k<6
        player_hurt=player.alive and not player.escaped and player.hp<player.max_hp
        near_player=math.dist((self.tx,self.ty),(player.tx,player.ty))<HEAL_RANGE

        if fleeing:
            self.assigned_gen=None
            if self.path_timer<=0:
                self.path_timer=0.8
                kx,ky=min(killer_tiles,key=lambda kt:math.dist((self.tx,self.ty),kt))
                far=[(random.randint(0,COLS-1),random.randint(0,ROWS-1)) for _ in range(14)]
                far=[t for t in far if grid[t[1]][t[0]]==FLOOR and math.dist(t,(kx,ky))>8]
                if far: self.target=random.choice(far)
        elif player_hurt and math.dist((self.tx,self.ty),(player.tx,player.ty))<6:
            if near_player:
                self.healing=True
                player.hp=min(player.max_hp, player.hp+HEAL_RATE*dt)
                self.target=None
            else:
                if self.path_timer<=0:
                    self.path_timer=0.5; self.target=player.tile
        elif exit_open:
            self.target=exit_pos
        else:
            if self.path_timer<=0:
                self.path_timer=1.5
                undone=[g for g in generators if not g.done]
                if undone:
                    g=min(undone,key=lambda g:math.dist((self.tx,self.ty),(g.tx,g.ty)))
                    self.assigned_gen=g; self.target=(g.tx,g.ty)

        if self.target and not self.healing:
            nxt=bfs_path(grid,self.tile,self.target)
            if nxt:
                nx,ny=nxt; dx,dy=nx-self.tx,ny-self.ty
                d=math.sqrt(dx*dx+dy*dy) or 1
                self.tx+=(dx/d)*self.speed*dt; self.ty+=(dy/d)*self.speed*dt

        if not exit_open and self.assigned_gen and not self.assigned_gen.done:
            if math.dist((self.tx,self.ty),(self.assigned_gen.tx,self.assigned_gen.ty))<1.5:
                self.repairing=True; self.assigned_gen.active=True

        if exit_open and self.target==exit_pos:
            if math.dist((self.tx,self.ty),exit_pos)<1.2: self.escaped=True

    def draw(self,surf,small_font):
        if self.escaped: return
        if not self.alive:
            # Draw ghost + countdown timer at spawn location
            px2=int(self.spawn_tx*TILE+TILE//2); py2=int(self.spawn_ty*TILE+TILE//2+HUD_H)
            gs=pygame.Surface((36,36),pygame.SRCALPHA)
            pygame.draw.circle(gs,(*self.color,55),(18,18),16)
            surf.blit(gs,(px2-18,py2-18))
            t=math.ceil(self.respawn_timer)
            cd=small_font.render(f"{self.name} {t}s",True,self.color)
            surf.blit(cd,(px2-cd.get_width()//2,py2-10))
            return
        px2=int(self.tx*TILE+TILE//2); py2=int(self.ty*TILE+TILE//2+HUD_H)
        draw_survivor_sprite(surf,px2,py2,self.color,self.name[0],self.frame,self.healing)
        lbl=small_font.render(self.name,True,self.color)
        surf.blit(lbl,(px2-lbl.get_width()//2,py2-26))
        if self.repairing:
            pygame.draw.circle(surf,YELLOW,(px2+12,py2-18),4)
        if self.healing:
            htxt=small_font.render("+HP",True,GREEN)
            surf.blit(htxt,(px2-10,py2-36))


# â”€â”€ Player â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class Player:
    def __init__(self,tx,ty):
        self.tx=float(tx); self.ty=float(ty)
        self.speed=4.5; self.alive=True; self.escaped=False
        self.repairing=False; self.slowed_timer=0.0
        self.hp=float(MAX_HP); self.max_hp=MAX_HP
        self.hit_timer=0.0    # cooldown between hits
        self.stun_cd=0.0      # cooldown on stun ability
        self.flash_timer=0.0  # red flash when hit
        self.frame=0
        self.equip={}  # {"helmet":item, "armor":item, "weapon":item}
    @property
    def tile(self): return (int(round(self.tx)),int(round(self.ty)))

    def update(self,dt,grid,keys,generators,exit_open,exit_pos):
        if not self.alive or self.escaped: return
        self.frame+=1
        self.slowed_timer=max(0,self.slowed_timer-dt)
        self.hit_timer=max(0,self.hit_timer-dt)
        self.stun_cd=max(0,self.stun_cd-dt)
        self.flash_timer=max(0,self.flash_timer-dt)
        spd=self.speed*(0.45 if self.slowed_timer>0 else 1.0)
        dx=dy=0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy-=1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy+=1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx-=1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx+=1
        if dx or dy:
            ln=math.sqrt(dx*dx+dy*dy)
            nx=self.tx+(dx/ln)*spd*dt; ny=self.ty+(dy/ln)*spd*dt
            if 0<=int(nx)<COLS and 0<=int(self.ty)<ROWS and grid[int(self.ty)][int(nx)]==FLOOR: self.tx=nx
            if 0<=int(self.tx)<COLS and 0<=int(ny)<ROWS and grid[int(ny)][int(self.tx)]==FLOOR: self.ty=ny
        self.repairing=False
        if keys[pygame.K_e]:
            for g in generators:
                if not g.done and math.dist((self.tx,self.ty),(g.tx,g.ty))<1.8:
                    g.active=True; self.repairing=True; break
        if exit_open and math.dist((self.tx,self.ty),exit_pos)<1.5: self.escaped=True
        if self.hp<=0: self.alive=False

    def take_hit(self):
        if self.hit_timer<=0:
            self.hp-=1; self.hit_timer=HIT_CD; self.flash_timer=0.4

    def update_city(self,dt,grid,keys,gw,gh):
        if not self.alive: return
        self.frame+=1
        self.flash_timer=max(0,self.flash_timer-dt)
        self.hit_timer=max(0,self.hit_timer-dt)
        self.stun_cd=max(0,self.stun_cd-dt)
        spd=self.speed
        dx=dy=0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy-=1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy+=1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx-=1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx+=1
        if dx or dy:
            ln=math.sqrt(dx*dx+dy*dy)
            nx=self.tx+(dx/ln)*spd*dt; ny=self.ty+(dy/ln)*spd*dt
            blocked={C_BWALL,C_WATER}
            if 0<=int(nx)<gw and 0<=int(self.ty)<gh and grid[int(self.ty)][int(nx)] not in blocked: self.tx=nx
            if 0<=int(self.tx)<gw and 0<=int(ny)<gh and grid[int(ny)][int(self.tx)] not in blocked: self.ty=ny
            self.tx=max(0,min(gw-1,self.tx)); self.ty=max(0,min(gh-1,self.ty))

    def draw_city(self,surf,cam_x,cam_y):
        if not self.alive: return
        sx=int((self.tx-cam_x)*TILE+TILE//2); sy=int((self.ty-cam_y)*TILE+TILE//2+HUD_H)
        draw_player_sprite(surf,sx,sy,flash=self.flash_timer>0,equip=self.equip)
        for i in range(self.max_hp):
            col=RED if i<int(self.hp+0.99) else (50,20,20)
            hx=sx-22+i*16; hy=sy-30
            pygame.draw.rect(surf,col,(hx,hy+2,5,5))
            pygame.draw.rect(surf,col,(hx+5,hy+2,5,5))
            pygame.draw.rect(surf,col,(hx+1,hy,9,4))
            pygame.draw.rect(surf,col,(hx+2,hy+6,7,3))
            pygame.draw.rect(surf,col,(hx+3,hy+8,5,2))
            pygame.draw.rect(surf,col,(hx+4,hy+9,3,1))

    def draw(self,surf):
        if not self.alive or self.escaped: return
        px2=int(self.tx*TILE+TILE//2); py2=int(self.ty*TILE+TILE//2+HUD_H)
        draw_player_sprite(surf,px2,py2,
            repairing=self.repairing,
            slowed=self.slowed_timer>0,
            flash=self.flash_timer>0,
            equip=self.equip)
        # HP hearts above head
        for i in range(self.max_hp):
            col=RED if i<int(self.hp+0.99) else (50,20,20)
            hx=px2-22+i*16; hy=py2-30
            pygame.draw.rect(surf,col,(hx,hy+2,5,5))
            pygame.draw.rect(surf,col,(hx+5,hy+2,5,5))
            pygame.draw.rect(surf,col,(hx+1,hy,9,4))
            pygame.draw.rect(surf,col,(hx+2,hy+6,7,3))
            pygame.draw.rect(surf,col,(hx+3,hy+8,5,2))
            pygame.draw.rect(surf,col,(hx+4,hy+9,3,1))

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# KILLER SKINS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class KillerBase:
    name="???"; title="The Unknown"; description="A mysterious threat."
    ability_label=""; body_color=DARK_RED; eye_color=RED; accent=RED
    speed=2.4; radius=13
    def __init__(self,tx,ty):
        self.tx=float(tx); self.ty=float(ty)
        self.target=None; self.path_timer=0.0
        self.stunned=0.0; self.frame=0
    @property
    def tile(self): return (int(round(self.tx)),int(round(self.ty)))
    def _pick(self,survivors,player):
        pool=[s for s in survivors if s.alive and not s.escaped]
        if player.alive and not player.escaped: pool.append(player)
        if pool: self.target=min(pool,key=lambda s:math.dist((self.tx,self.ty),(s.tx,s.ty)))
    def _move(self,dt,grid):
        if not self.target or not getattr(self.target,'alive',True): return
        nxt=bfs_path(grid,self.tile,self.target.tile)
        if nxt:
            nx,ny=nxt; dx,dy=nx-self.tx,ny-self.ty; d=math.sqrt(dx*dx+dy*dy) or 1
            self.tx+=(dx/d)*self.speed*dt; self.ty+=(dy/d)*self.speed*dt
    def _hit(self,survivors,player,rng=1.0):
        for s in survivors:
            if s.alive and not s.escaped and math.dist((self.tx,self.ty),(s.tx,s.ty))<rng:
                s.alive=False; s.respawn_timer=10.0  # respawn in 10 seconds
        if player.alive and not player.escaped and math.dist((self.tx,self.ty),(player.tx,player.ty))<rng:
            player.take_hit()
    def update(self,dt,grid,survivors,player):
        self.frame+=1
        if self.stunned>0: self.stunned-=dt; return
        self.path_timer-=dt
        if self.path_timer<=0: self.path_timer=0.5; self._pick(survivors,player)
        self._move(dt,grid); self._hit(survivors,player)
    def draw(self,surf):
        px2=int(self.tx*TILE+TILE//2); py2=int(self.ty*TILE+TILE//2+HUD_H)
        draw_killer_sprite(surf,px2,py2,self.name,stunned=self.stunned>0,frame=self.frame)
        # Name tag
        if self.stunned>0:
            stun_surf=pygame.font.SysFont("consolas",11,bold=True).render("STUNNED",True,YELLOW)
            surf.blit(stun_surf,(px2-stun_surf.get_width()//2,py2-30))

class KillerWraith(KillerBase):
    name="WRAITH"; title="The Wraith"
    description="Relentless and rage-fueled.\nThe longer it hunts, the faster it gets."
    ability_label="BLOODLUST: speeds up while chasing"
    body_color=(160,20,20); eye_color=(255,90,90); accent=(220,50,50); speed=3.0
    def __init__(self,tx,ty):
        super().__init__(tx,ty); self.chase_time=0.0; self.bloodlust=1.0
    def update(self,dt,grid,survivors,player):
        self.frame+=1
        if self.stunned>0: self.stunned-=dt; return
        self.path_timer-=dt
        if self.path_timer<=0:
            self.path_timer=0.3; old=self.target; self._pick(survivors,player)
            if self.target is not old: self.chase_time=0.0; self.bloodlust=1.0
        if self.target and getattr(self.target,'alive',True):
            self.chase_time+=dt; self.bloodlust=min(1.7,1.0+self.chase_time*0.09)
            self.speed=3.0*self.bloodlust; self._move(dt,grid)
        self._hit(survivors,player)
    def draw(self,surf):
        if self.bloodlust>1.3:
            px2=int(self.tx*TILE+TILE//2); py2=int(self.ty*TILE+TILE//2+HUD_H)
            gr=int(18+8*(self.bloodlust-1.3)/0.4)
            gs=pygame.Surface((gr*2,gr*2),pygame.SRCALPHA)
            pygame.draw.circle(gs,(100,0,0,70),(gr,gr),gr); surf.blit(gs,(px2-gr,py2-gr))
        super().draw(surf)

class KillerPhantom(KillerBase):
    name="PHANTOM"; title="The Phantom"
    description="Ghostly and patient.\nTouch its aura and your legs freeze."
    ability_label="CHILL TOUCH: slows you when nearby"
    body_color=(30,30,90); eye_color=(130,180,255); accent=(80,100,220); speed=2.3
    CHILL=2.8
    def update(self,dt,grid,survivors,player):
        self.frame+=1
        if self.stunned>0: self.stunned-=dt; return
        self.path_timer-=dt
        if self.path_timer<=0: self.path_timer=0.5; self._pick(survivors,player)
        self._move(dt,grid)
        if player.alive and not player.escaped:
            if math.dist((self.tx,self.ty),(player.tx,player.ty))<self.CHILL:
                player.slowed_timer=max(player.slowed_timer,2.5)
        self._hit(survivors,player)
    def draw(self,surf):
        px2=int(self.tx*TILE+TILE//2); py2=int(self.ty*TILE+TILE//2+HUD_H)
        aura=pygame.Surface((100,100),pygame.SRCALPHA)
        pygame.draw.circle(aura,(60,80,200,30),(50,50),50); surf.blit(aura,(px2-50,py2-50))
        super().draw(surf)

class KillerStalker(KillerBase):
    name="STALKER"; title="The Stalker"
    description="It lurks in darkness.\nYou won't see it until it's too late."
    ability_label="SHADOW VEIL: invisible until 4 tiles away"
    body_color=(12,12,15); eye_color=(0,255,110); accent=(0,180,75); speed=2.1
    REVEAL=4.0
    def __init__(self,tx,ty): super().__init__(tx,ty); self._alpha=18
    def update(self,dt,grid,survivors,player):
        self.frame+=1
        if self.stunned>0: self.stunned-=dt; return
        self.path_timer-=dt
        if self.path_timer<=0: self.path_timer=0.55; self._pick(survivors,player)
        self._move(dt,grid)
        if player.alive:
            d=math.dist((self.tx,self.ty),(player.tx,player.ty))
            self._alpha=18 if d>self.REVEAL else int(20+235*(1-d/self.REVEAL))
        else: self._alpha=255
        self._hit(survivors,player)
    def draw(self,surf):
        px2=int(self.tx*TILE+TILE//2); py2=int(self.ty*TILE+TILE//2+HUD_H)
        s=pygame.Surface((40,40),pygame.SRCALPHA)
        # Draw a simple alpha ghost for stalker
        pygame.draw.circle(s,(*self.body_color,self._alpha),(20,20),18)
        pygame.draw.circle(s,(*self.accent,self._alpha),(20,20),18,2)
        surf.blit(s,(px2-20,py2-20))
        # Eyes always glow slightly
        eye_a=max(60,self._alpha)
        es=pygame.Surface((8,4),pygame.SRCALPHA)
        pygame.draw.rect(es,(*self.eye_color,eye_a),(0,0,3,3))
        pygame.draw.rect(es,(*self.eye_color,eye_a),(5,0,3,3))
        surf.blit(es,(px2-4,py2-4))
        if self.stunned>0:
            stun_surf=pygame.font.SysFont("consolas",11,bold=True).render("STUNNED",True,YELLOW)
            surf.blit(stun_surf,(px2-stun_surf.get_width()//2,py2-30))

class KillerBlight(KillerBase):
    name="BLIGHT"; title="The Blight"
    description="Corrupted void entity.\nIt can teleport anywhere without warning."
    ability_label="VOID BLINK: teleports near a survivor every 10s"
    body_color=(65,0,95); eye_color=(195,45,255); accent=(160,0,200); speed=2.2
    BLINK_CD=10.0
    def __init__(self,tx,ty):
        super().__init__(tx,ty); self.blink_timer=self.BLINK_CD; self.flash=0.0
    def update(self,dt,grid,survivors,player):
        self.frame+=1
        if self.stunned>0: self.stunned-=dt; return
        self.path_timer-=dt; self.blink_timer-=dt; self.flash=max(0,self.flash-dt)
        if self.path_timer<=0: self.path_timer=0.5; self._pick(survivors,player)
        if self.blink_timer<=0:
            self.blink_timer=self.BLINK_CD; self.flash=0.5
            pool=[s for s in survivors if s.alive and not s.escaped]
            if player.alive and not player.escaped: pool.append(player)
            if pool:
                tgt=random.choice(pool); angle=random.uniform(0,2*math.pi)
                dist=random.uniform(2,3)
                bx=int(tgt.tx+math.cos(angle)*dist); by=int(tgt.ty+math.sin(angle)*dist)
                bx=max(0,min(COLS-1,bx)); by=max(0,min(ROWS-1,by))
                if grid[by][bx]==FLOOR: self.tx=float(bx); self.ty=float(by)
        self._move(dt,grid); self._hit(survivors,player)
    def draw(self,surf):
        px2=int(self.tx*TILE+TILE//2); py2=int(self.ty*TILE+TILE//2+HUD_H)
        if self.flash>0:
            fr=int(38*self.flash/0.5); fs=pygame.Surface((fr*2,fr*2),pygame.SRCALPHA)
            pygame.draw.circle(fs,(180,0,255,150),(fr,fr),fr); surf.blit(fs,(px2-fr,py2-fr))
        super().draw(surf)
        rem=self.blink_timer/self.BLINK_CD
        if rem>0.02:
            try: pygame.draw.arc(surf,(180,0,255),(px2-20,py2-20,40,40),math.radians(-90),math.radians(-90+360*(1-rem)),2)
            except: pass

class KillerReaper(KillerBase):
    name="REAPER"; title="The Reaper"
    description="Every kill makes it stronger.\nLet it harvest enough and nothing stops it."
    ability_label="SOUL HARVEST: +0.4 speed per kill"
    body_color=(8,8,8); eye_color=(255,200,0); accent=(200,160,0); speed=1.9
    BASE_SPEED=1.9
    def __init__(self,tx,ty): super().__init__(tx,ty); self.kills=0
    def update(self,dt,grid,survivors,player):
        self.frame+=1
        if self.stunned>0: self.stunned-=dt; return
        self.path_timer-=dt
        if self.path_timer<=0: self.path_timer=0.45; self._pick(survivors,player)
        self._move(dt,grid)
        before=sum(1 for s in survivors if not s.alive); was=player.alive
        self._hit(survivors,player)
        after=sum(1 for s in survivors if not s.alive)
        nk=(after-before)+(1 if was and not player.alive else 0)
        if nk>0: self.kills+=nk; self.speed=self.BASE_SPEED+self.kills*0.4
    def draw(self,surf):
        px2=int(self.tx*TILE+TILE//2); py2=int(self.ty*TILE+TILE//2+HUD_H)
        if self.kills>0:
            gr=20+self.kills*3
            gs=pygame.Surface((gr*2,gr*2),pygame.SRCALPHA)
            gc=(min(255,50+self.kills*50),min(255,35+self.kills*35),0)
            pygame.draw.circle(gs,(*gc,75),(gr,gr),gr); surf.blit(gs,(px2-gr,py2-gr))
        super().draw(surf)

ALL_KILLERS=[KillerWraith,KillerPhantom,KillerStalker,KillerBlight,KillerReaper]


# â”€â”€ City Map â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def generate_city():
    grid=[[C_GRASS]*CITY_W for _ in range(CITY_H)]
    # Main roads
    for r in range(CITY_H):
        for c in range(CITY_W//2-1,CITY_W//2+2): grid[r][c]=C_PATH
    for c in range(CITY_W):
        for r in range(CITY_H//2-1,CITY_H//2+2): grid[r][c]=C_PATH
    # Central plaza
    cx2,cy2=CITY_W//2,CITY_H//2
    for r in range(cy2-4,cy2+5):
        for c in range(cx2-5,cx2+6): grid[r][c]=C_PATH
    # Fountain
    for r in range(cy2-1,cy2+2):
        for c in range(cx2-1,cx2+2): grid[r][c]=C_WATER
    # Buildings
    bldgs=[
        (5,5,8,5),(20,5,8,5),(60,5,8,5),  # top row: bakery, blacksmith, potion shop
        (5,20,6,4),(65,20,6,4),             # mid row: west house, library
        (5,40,7,5),(60,40,8,5),             # south row: pet shop, south house
        (36,10,9,5),                         # inn (near center north)
        (15,15,6,4),(50,15,6,4),            # extra houses
        (15,35,6,4),(55,35,6,4),            # more houses south
        (70,1,10,7),                            # YOUR PRIVATE HOUSE (NE corner)
    ]
    for bx,by,bw,bh in bldgs:
        for r in range(by,min(by+bh,CITY_H)):
            for c in range(bx,min(bx+bw,CITY_W)):
                if r==by or r==by+bh-1 or c==bx or c==bx+bw-1: grid[r][c]=C_BWALL
                else: grid[r][c]=C_BFLOOR
        if by+bh-1<CITY_H: grid[by+bh-1][bx+bw//2]=C_BFLOOR
    # Your private house beds (inside house at 70,1,10,7)
    for r in [3,4]:
        for c in [76,77]: grid[r][c]=C_BED
    # Path to your house
    for c in range(65,71):
        if grid[3][c]==C_GRASS: grid[3][c]=C_PATH
    for r in range(1,8):
        if grid[r][69]==C_GRASS: grid[r][69]=C_PATH
    # Side paths
    for r in range(5,CITY_H-5):
        for c in range(4,6):
            if grid[r][c]==C_GRASS: grid[r][c]=C_PATH
        for c in range(CITY_W-6,CITY_W-4):
            if grid[r][c]==C_GRASS: grid[r][c]=C_PATH
    # Arena area (south)
    for r in range(CITY_H-15,CITY_H-3):
        for c in range(cx2-10,cx2+11):
            if 0<=c<CITY_W and grid[r][c]==C_GRASS: grid[r][c]=C_PATH
    # Portal area
    px2,py2=PORTAL_POS
    for r in range(py2-2,min(py2+3,CITY_H)):
        for c in range(px2-2,min(px2+3,CITY_W)):
            if grid[r][c]==C_GRASS: grid[r][c]=C_PATH
    # â”€â”€ BIOMES â”€â”€
    # Desert (NW corner)
    for r in range(0,15):
        for c in range(0,18):
            if grid[r][c]==C_GRASS: grid[r][c]=C_SAND
    # Snow (NE area, below house)
    for r in range(9,20):
        for c in range(60,CITY_W):
            if grid[r][c]==C_GRASS: grid[r][c]=C_SNOW
    # Mushroom Forest (SW)
    for r in range(35,CITY_H):
        for c in range(0,18):
            if grid[r][c]==C_GRASS: grid[r][c]=C_MUSHROOM
    # Swamp (SE)
    for r in range(35,CITY_H):
        for c in range(60,CITY_W):
            if grid[r][c]==C_GRASS: grid[r][c]=C_SWAMP
    # Dark forest (south center fringes)
    for r in range(CITY_H-5,CITY_H):
        for c in range(18,60):
            if grid[r][c]==C_GRASS: grid[r][c]=C_DARKGRASS
    # Small lava pools in arena
    for lr,lc in [(47,32),(47,48),(52,35),(52,45)]:
        if 0<=lr<CITY_H and 0<=lc<CITY_W and grid[lr][lc]!=C_PATH:
            grid[lr][lc]=C_LAVA
    return grid


# â”€â”€ City NPC â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class CityNPC:
    def __init__(self,d):
        self.tx=float(d["tx"]); self.ty=float(d["ty"])
        self.home_tx=float(d["tx"]); self.home_ty=float(d["ty"])
        self.name=d["name"]; self.color=d["color"]
        self.dialog=d["dialog"]; self.heals=d.get("heals",False)
        self.is_shop=d.get("is_shop",False); self.frame=random.randint(0,200)
        self.shop_type=d.get("shop_type",None)
        self.stay=d.get("stay",False)
        self.wander_timer=random.uniform(1.0,4.0)
        self.wander_dx=0.0; self.wander_dy=0.0
        self.speed=random.uniform(0.6,1.2)
    def update(self,dt,grid):
        if self.stay: return  # Chef/Butler stay put
        self.wander_timer-=dt
        if self.wander_timer<=0:
            self.wander_timer=random.uniform(1.5,5.0)
            if random.random()<0.4:
                self.wander_dx=0.0; self.wander_dy=0.0  # pause
            else:
                a=random.uniform(0,2*math.pi)
                self.wander_dx=math.cos(a); self.wander_dy=math.sin(a)
        if self.wander_dx or self.wander_dy:
            nx=self.tx+self.wander_dx*self.speed*dt
            ny=self.ty+self.wander_dy*self.speed*dt
            blocked={C_BWALL,C_WATER}
            gw=len(grid[0]); gh=len(grid)
            if 0<=int(nx)<gw and 0<=int(self.ty)<gh and grid[int(self.ty)][int(nx)] not in blocked: self.tx=nx
            if 0<=int(self.tx)<gw and 0<=int(ny)<gh and grid[int(ny)][int(self.tx)] not in blocked: self.ty=ny
            # Don't wander too far from home
            if math.dist((self.tx,self.ty),(self.home_tx,self.home_ty))>5:
                self.wander_dx=self.home_tx-self.tx; self.wander_dy=self.home_ty-self.ty
                d2=math.sqrt(self.wander_dx**2+self.wander_dy**2) or 1
                self.wander_dx/=d2; self.wander_dy/=d2
    def draw(self,surf,cam_x,cam_y,small_font):
        sx=int((self.tx-cam_x)*TILE+TILE//2); sy=int((self.ty-cam_y)*TILE+TILE//2+HUD_H)
        if sx<-30 or sx>GAME_W+30 or sy<HUD_H-30 or sy>SCREEN_H+30: return
        self.frame+=1
        draw_survivor_sprite(surf,sx,sy,self.color,self.name[0],self.frame)
        lbl=small_font.render(self.name,True,self.color)
        surf.blit(lbl,(sx-lbl.get_width()//2,sy-26))
        pygame.draw.rect(surf,YELLOW,(sx-2,sy-32,4,4))  # interact indicator


# â”€â”€ City Boss â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class CityBoss:
    def __init__(self,d):
        self.name=d["name"]; self.max_hp=d["hp"]; self.hp=d["hp"]
        self.speed=d["speed"]; self.damage=d["damage"]
        self.color=d["color"]; self.gold_reward=d["gold"]
        self.tx=float(d["tx"]); self.ty=float(d["ty"])
        self.alive=True; self.aggro=False; self.attack_cd=0.0
        self.frame=0; self.rewarded=False
    @property
    def tile(self): return (int(round(self.tx)),int(round(self.ty)))
    def update(self,dt,grid,player):
        if not self.alive: return
        self.frame+=1; self.attack_cd=max(0,self.attack_cd-dt)
        dist=math.dist((self.tx,self.ty),(player.tx,player.ty))
        # Player's house is a safe zone â€” bosses can't enter or attack
        player_in_house=70<=player.tx<=80 and 0<=player.ty<=8
        boss_near_house=70<=self.tx<=80 and 0<=self.ty<=8
        if player_in_house:
            self.aggro=False
            # Push boss away from house if somehow inside
            if boss_near_house:
                self.tx=max(self.tx,81.0) if self.tx>75 else min(self.tx,69.0)
                self.ty=max(self.ty,9.0)
            return
        if dist<8: self.aggro=True
        if dist>15: self.aggro=False
        if self.aggro and player.alive:
            dx2=player.tx-self.tx; dy2=player.ty-self.ty
            d2=math.sqrt(dx2*dx2+dy2*dy2) or 1
            nx=self.tx+(dx2/d2)*self.speed*dt; ny=self.ty+(dy2/d2)*self.speed*dt
            # Block bosses from entering the house zone
            if 69<=nx<=81 and ny<=9:
                return
            ix,iy=int(nx),int(ny)
            blocked={C_BWALL,C_WATER}
            gw=len(grid[0]); gh=len(grid)
            if 0<=ix<gw and 0<=int(self.ty)<gh and grid[int(self.ty)][ix] not in blocked: self.tx=nx
            if 0<=int(self.tx)<gw and 0<=iy<gh and grid[iy][int(self.tx)] not in blocked: self.ty=ny
            if dist<1.2 and self.attack_cd<=0 and not player_in_house:
                player.take_hit(); self.attack_cd=2.0
    def take_damage(self):
        self.hp-=1
        if self.hp<=0: self.alive=False; return True
        return False
    def draw(self,surf,cam_x,cam_y,font,small_font):
        if not self.alive: return
        sx=int((self.tx-cam_x)*TILE+TILE//2); sy=int((self.ty-cam_y)*TILE+TILE//2+HUD_H)
        if sx<-30 or sx>GAME_W+30 or sy<HUD_H-30 or sy>SCREEN_H+30: return
        S=2; ox=sx-16; oy=sy-16
        def p(x,y,c): pygame.draw.rect(surf,c,(ox+x*S,oy+y*S,S,S))
        t=self.frame*0.05
        n=self.name

        if n=="Goblin Chief":
            skin=(60,130,30); dark=(35,80,15); eyes=(255,40,40); teeth=(220,220,180)
            for r in range(2,15):
                for c in range(4,12): p(c,r,skin)
            for r in range(0,4):
                for c in range(5,11): p(c,r,dark)
            p(4,0,(40,100,20)); p(11,0,(40,100,20))  # pointed ears
            p(3,1,(40,100,20)); p(12,1,(40,100,20))
            p(6,3,eyes); p(7,3,eyes); p(9,3,eyes); p(10,3,eyes)
            p(7,5,teeth); p(8,5,teeth); p(6,5,teeth); p(9,5,teeth)  # fangs
            p(6,6,(20,60,10)); p(9,6,(20,60,10))  # tusks poke down
            for r in range(6,10): p(3,r,dark); p(12,r,dark)  # arms
            p(2,9,(120,100,40)); p(13,9,(120,100,40))  # clubs in hands
            for r in range(7,14): p(2,r,(120,100,40))  # club shaft
            for c in [4,6,8,10]: p(c,15,dark)

        elif n=="Stone Troll":
            body=(100,90,70); dark=(65,55,40); eyes=(200,30,30); moss=(50,90,40)
            for r in range(1,16):
                for c in range(3,13): p(c,r,body)
            for r in range(0,4):
                for c in range(4,12): p(c,r,dark)
            p(6,2,eyes); p(7,2,(60,10,10)); p(9,2,eyes); p(10,2,(60,10,10))
            p(7,4,(50,40,30)); p(8,4,(50,40,30)); p(9,4,(50,40,30))  # mouth crack
            for r in range(4,10): p(2,r,body); p(13,r,body)  # huge arms
            for r in range(6,12): p(1,r,body); p(14,r,body)
            p(5,6,moss); p(9,8,moss); p(7,11,moss); p(11,5,moss)  # moss patches
            for c in range(3,13): p(c,15,dark)

        elif n=="Shadow Dragon":
            body=(45,15,80); wing=(80,30,140); eyes=(255,50,255); fire=(255,100,30)
            for r in range(3,14):
                for c in range(4,12): p(c,r,body)
            for r in range(0,5):
                for c in range(5,11): p(c,r,body)
            p(6,2,eyes); p(7,2,eyes); p(9,2,eyes); p(10,2,eyes)  # glowing eyes
            p(7,4,fire); p(8,4,fire); p(9,4,fire)  # fire breath
            p(6,5,fire); p(10,5,(200,60,15))
            # Wings
            for r in range(2,8): p(2,r,wing); p(1,r,wing); p(0,r+1,wing)
            for r in range(2,8): p(13,r,wing); p(14,r,wing); p(15,r+1,wing)
            # Horns
            p(5,0,(70,20,100)); p(4,0,(50,10,80)); p(10,0,(70,20,100)); p(11,0,(50,10,80))
            # Tail
            for c in range(4,8): p(c,14,(35,10,65)); p(c-1,15,(35,10,65))
            p(2,15,fire); p(3,15,fire)  # tail fire tip

        elif n=="Fire Imp":
            body=(200,60,10); flame=(255,180,30); eyes=(255,255,0); dark=(120,30,5)
            for r in range(3,13):
                for c in range(5,11): p(c,r,body)
            for r in range(0,4):
                for c in range(6,10): p(c,r,flame)
            p(5,0,flame); p(10,0,flame); p(4,1,(255,220,50)); p(11,1,(255,220,50))
            p(6,4,eyes); p(9,4,eyes)
            p(7,6,dark); p(8,6,dark)  # grin
            for r in range(6,12): p(4,r,body); p(11,r,body)  # thin arms
            # Fire trail
            fi=int(3*math.sin(t*4))
            p(7,13,flame); p(8,13,flame); p(7+fi,14,(255,100,20)); p(8-fi,15,(255,60,10))
            for c in [5,7,9]: p(c,14,dark)

        elif n=="Ice Golem":
            body=(140,190,220); ice=(180,220,255); dark=(60,100,140); crack=(220,240,255)
            for r in range(1,16):
                for c in range(3,13): p(c,r,body)
            for r in range(0,3):
                for c in range(4,12): p(c,r,ice)
            p(6,1,(40,80,180)); p(7,1,(40,80,180)); p(9,1,(40,80,180)); p(10,1,(40,80,180))  # deep eyes
            p(7,3,dark); p(8,3,dark)  # mouth
            for r in range(3,12): p(2,r,body); p(13,r,body)  # thick arms
            for r in range(5,10): p(1,r,ice); p(14,r,ice)  # ice spikes
            p(5,5,crack); p(9,7,crack); p(7,10,crack); p(11,4,crack)  # cracks
            p(0,7,ice); p(15,7,ice)  # ice shards
            for c in range(3,13): p(c,15,dark)

        elif n=="Dark Knight":
            armor=(25,25,35); visor=(8,8,12); eyes=(255,0,0); cape=(15,10,25); blade=(200,200,210)
            for r in range(2,14):
                for c in range(4,12): p(c,r,armor)
            for r in range(0,4):
                for c in range(5,11): p(c,r,armor)
            p(5,0,visor); p(6,0,visor); p(9,0,visor); p(10,0,visor)  # helmet horns
            p(6,2,eyes); p(9,2,eyes)  # glowing red eyes
            p(7,3,visor); p(8,3,visor)  # visor slit
            for r in range(5,13): p(3,r,cape); p(12,r,cape)  # cape
            for r in range(4,9): p(2,r,cape); p(13,r,cape)
            # Sword
            for r in range(1,12): p(14,r,blade)
            p(14,0,(240,240,250)); p(15,5,blade); p(15,6,blade)
            # Legs
            for c in [5,6,9,10]: p(c,14,armor); p(c,15,(15,15,20))

        elif n=="Bone Reaver":
            bone=(210,200,170); dark=(40,30,20); eyes=(0,255,100); rot=(130,100,60)
            for r in range(2,14):
                for c in range(4,12): p(c,r,bone)
            for r in range(0,3):
                for c in range(5,11): p(c,r,bone)
            # Skull face
            p(6,1,dark); p(7,1,dark); p(9,1,dark); p(10,1,dark)  # empty sockets
            p(6,1,eyes); p(10,1,eyes)  # ghostly glow inside
            p(7,3,dark); p(8,3,dark)  # nose hole
            for c in range(6,10): p(c,4,dark)  # teeth line
            p(6,5,bone); p(8,5,bone); p(10,5,bone)  # teeth
            # Ribs visible
            for r in [6,8,10]: p(5,r,dark); p(10,r,dark)
            # Scythe
            for r in range(2,13): p(13,r,rot); p(14,r,rot)
            for c in range(9,15): p(c,2,bone)
            p(14,3,bone); p(13,4,bone)
            # Tattered robe
            for c in [4,6,8,10]: p(c,14,rot); p(c,15,dark)

        elif n=="Venom Queen":
            body=(50,160,40); dark=(25,80,20); eyes=(255,255,0); fang=(240,240,220); venom=(120,255,50)
            for r in range(2,14):
                for c in range(4,12): p(c,r,body)
            for r in range(0,3):
                for c in range(5,11): p(c,r,dark)
            p(5,0,body); p(10,0,body)  # crown-like head
            p(4,1,venom); p(11,1,venom)
            p(6,1,eyes); p(7,1,eyes); p(9,1,eyes); p(10,1,eyes)  # slitted eyes
            p(7,3,fang); p(8,3,fang)  # fangs
            p(7,4,venom); p(8,4,venom)  # dripping venom
            # Snake body lower half
            for r in range(10,16):
                for c in range(3,13):
                    sc=(40,140,30) if (r+c)%3==0 else (30,110,20)
                    p(c,r,sc)
            # Tail
            p(3,14,dark); p(2,15,dark); p(1,15,venom)
            p(12,14,dark); p(13,15,dark); p(14,15,venom)
            # Venom drip particles
            vi=int(2*math.sin(t*3))
            p(7,5+vi,venom); p(8,6+vi,(80,200,30))

        else:
            # Fallback for unknown bosses
            pygame.draw.circle(surf,self.color,(sx,sy),14)
            pygame.draw.circle(surf,tuple(min(255,c+60) for c in self.color),(sx,sy),14,2)
            pygame.draw.circle(surf,RED,(sx-4,sy-3),3)
            pygame.draw.circle(surf,RED,(sx+4,sy-3),3)

        # Aggro aura
        if self.aggro:
            ar=int(20+3*math.sin(t*4))
            gs5=pygame.Surface((ar*2,ar*2),pygame.SRCALPHA)
            pygame.draw.circle(gs5,(*self.color,50),(ar,ar),ar)
            surf.blit(gs5,(sx-ar,sy-ar))
        # HP bar
        bw2=34; frac=self.hp/self.max_hp
        pygame.draw.rect(surf,(20,20,20),(sx-bw2//2,sy-26,bw2,5))
        pygame.draw.rect(surf,RED,(sx-bw2//2,sy-26,int(bw2*frac),5))
        pygame.draw.rect(surf,WHITE,(sx-bw2//2,sy-26,bw2,5),1)
        lbl=small_font.render(self.name,True,self.color)
        surf.blit(lbl,(sx-lbl.get_width()//2,sy-34))


# â”€â”€ Shop UI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def draw_shop(surf,font,big_font,small_font,gold,owned_items,equipped,shop_cursor,player_equip):
    surf.fill((20,15,10))
    t=big_font.render("SHOP",True,GOLD_COIN_COLOR)
    surf.blit(t,t.get_rect(center=(SCREEN_W//2,40)))
    surf.blit(font.render(f"Gold: {gold}g",True,GOLD_COIN_COLOR),(SCREEN_W//2-50,70))
    col_w=420; start_x=(SCREEN_W-col_w*2)//2
    y=110
    for i,item in enumerate(SHOP_ITEMS):
        ci=i%2; row=i//2
        ix=start_x+ci*col_w; iy=y+row*56
        sel=(i==shop_cursor); owned=item["id"] in owned_items
        eq=equipped.get(item["slot"])==item["id"]
        bg=(50,45,30) if sel else (30,25,15)
        if eq: bg=(30,50,30)
        pygame.draw.rect(surf,bg,(ix,iy,col_w-10,50),border_radius=5)
        if sel: pygame.draw.rect(surf,GOLD_COIN_COLOR,(ix,iy,col_w-10,50),2,border_radius=5)
        pygame.draw.rect(surf,item["color"],(ix+8,iy+8,20,20))
        pygame.draw.rect(surf,WHITE,(ix+8,iy+8,20,20),1)
        nc=GREEN if owned else WHITE
        surf.blit(font.render(item["name"],True,nc),(ix+36,iy+6))
        if owned:
            if eq: surf.blit(small_font.render("[EQUIPPED]",True,GREEN),(ix+36,iy+24))
            else: surf.blit(small_font.render("[OWNED] ENTER=equip",True,(150,150,100)),(ix+36,iy+24))
        else:
            cc=WHITE if gold>=item["cost"] else RED
            surf.blit(small_font.render(f'{item["cost"]}g - {item["desc"]}',True,cc),(ix+36,iy+24))
        surf.blit(small_font.render(f'[{item["slot"].upper()}]',True,GRAY),(ix+col_w-80,iy+8))
    # Player preview with current cursor item
    preview=dict(player_equip)
    ci2=SHOP_ITEMS[shop_cursor]
    preview[ci2["slot"]]=ci2
    tmp=pygame.Surface((64,64),pygame.SRCALPHA); tmp.fill((0,0,0,0))
    draw_player_sprite(tmp,32,32+16,equip=preview)
    big2=pygame.transform.scale(tmp,(128,128))
    surf.blit(big2,(SCREEN_W//2-64,SCREEN_H-210))
    surf.blit(small_font.render("YOUR PREVIEW",True,GRAY),(SCREEN_W//2-40,SCREEN_H-220))
    inst=font.render("Arrows=browse  ENTER=buy/equip  ESC=leave",True,GRAY)
    surf.blit(inst,inst.get_rect(center=(SCREEN_W//2,SCREEN_H-30)))


# â”€â”€ Food / Consumable Shop UI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
STATE_FOOD_SHOP="food_shop"

def get_food_menu(shop_type):
    if shop_type=="chef":
        return [
            {"id":"chef_bread","name":"Fresh Baguette","cost":0,"desc":"Heals 1 HP â€” FREE!","heal":1},
            {"id":"chef_steak","name":"Chef's Grilled Steak","cost":0,"desc":"Heals 2 HP â€” FREE!","heal":2},
            {"id":"chef_feast","name":"Royal Feast","cost":0,"desc":"Full heal! â€” FREE!","heal":99},
            {"id":"chef_soup","name":"Healing Soup","cost":0,"desc":"Heals 3 HP â€” FREE!","heal":3},
            {"id":"chef_cookie","name":"Chocolate Cookie","cost":0,"desc":"Heals 1 HP â€” yummy!","heal":1},
            {"id":"chef_pie","name":"Golden Apple Pie","cost":0,"desc":"Full heal! â€” FREE!","heal":99},
        ]
    elif shop_type=="food":
        return [c for c in CONSUMABLES if c["id"] in ("bread","steak","feast","cookie")]
    elif shop_type=="potion":
        return [c for c in CONSUMABLES if "pot" in c["id"]]
    elif shop_type=="pet":
        return [c for c in CONSUMABLES if c["id"] in ("pet_snack","cookie")]
    elif shop_type=="inn":
        return [{"id":"inn_rest","name":"Rest & Meal","cost":40,"desc":"Full heal!","heal":99}]
    elif shop_type=="scroll":
        return [c for c in CONSUMABLES if c["id"] in ("speed_pot","shield_pot","stun_pot")]
    return CONSUMABLES

def draw_food_shop(surf,font,big_font,small_font,gold,menu,cursor,shop_name):
    surf.fill((15,12,8))
    t=big_font.render(shop_name,True,GOLD_COIN_COLOR)
    surf.blit(t,t.get_rect(center=(SCREEN_W//2,40)))
    surf.blit(font.render(f"Gold: {gold}g",True,GOLD_COIN_COLOR),(SCREEN_W//2-50,75))
    y=120
    for i,item in enumerate(menu):
        sel=(i==cursor)
        bg=(50,45,30) if sel else (25,20,12)
        bw2=500; bx2=(SCREEN_W-bw2)//2
        pygame.draw.rect(surf,bg,(bx2,y,bw2,44),border_radius=5)
        if sel: pygame.draw.rect(surf,GOLD_COIN_COLOR,(bx2,y,bw2,44),2,border_radius=5)
        surf.blit(font.render(item["name"],True,WHITE),(bx2+12,y+6))
        if item["cost"]==0:
            surf.blit(small_font.render("FREE! â€” "+item["desc"],True,GREEN),(bx2+12,y+24))
        else:
            cc=WHITE if gold>=item["cost"] else RED
            surf.blit(small_font.render(f'{item["cost"]}g  -  {item["desc"]}',True,cc),(bx2+12,y+24))
        if item.get("heal",0)>0:
            pygame.draw.rect(surf,(200,120,60),(bx2+bw2-40,y+10,24,24))
            pygame.draw.rect(surf,(255,200,100),(bx2+bw2-40,y+10,24,24),1)
        else:
            pygame.draw.rect(surf,(100,60,200),(bx2+bw2-40,y+10,24,24))
            pygame.draw.rect(surf,(180,140,255),(bx2+bw2-40,y+10,24,24),1)
        y+=52
    inst=font.render("Up/Down=browse  ENTER=buy  ESC=leave",True,GRAY)
    surf.blit(inst,inst.get_rect(center=(SCREEN_W//2,SCREEN_H-30)))


# â”€â”€ Draw City Arrows â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def draw_city_arrows(surf,cam_x,cam_y,small_font):
    for ax,ay,direction,label in CITY_ARROWS:
        sx=int((ax-cam_x)*TILE+TILE//2); sy=int((ay-cam_y)*TILE+TILE//2+HUD_H)
        if sx<-40 or sx>GAME_W+40 or sy<HUD_H-20 or sy>SCREEN_H+20: continue
        pygame.draw.circle(surf,(60,50,30),(sx,sy),12)
        pygame.draw.circle(surf,(120,100,60),(sx,sy),12,1)
        ac=(255,220,80)
        if direction=="up":
            pygame.draw.polygon(surf,ac,[(sx,sy-8),(sx-6,sy+2),(sx+6,sy+2)])
        elif direction=="down":
            pygame.draw.polygon(surf,ac,[(sx,sy+8),(sx-6,sy-2),(sx+6,sy-2)])
        elif direction=="left":
            pygame.draw.polygon(surf,ac,[(sx-8,sy),(sx+2,sy-6),(sx+2,sy+6)])
        elif direction=="right":
            pygame.draw.polygon(surf,ac,[(sx+8,sy),(sx-2,sy-6),(sx-2,sy+6)])
        lbl=small_font.render(label,True,(255,230,120))
        surf.blit(lbl,(sx-lbl.get_width()//2,sy+14))


# â”€â”€ City HUD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def draw_city_hud(surf,font,small_font,gold,player,bosses):
    pygame.draw.rect(surf,(8,8,16),(0,0,GAME_W,HUD_H))
    pygame.draw.line(surf,GRAY,(0,HUD_H),(GAME_W,HUD_H),1)
    surf.blit(font.render("HAVEN CITY",True,CYAN),(8,12))
    # Gold
    pygame.draw.circle(surf,GOLD_COIN_COLOR,(160,20),7)
    pygame.draw.circle(surf,(180,150,0),(160,20),7,1)
    surf.blit(font.render(f"{gold}",True,GOLD_COIN_COLOR),(170,12))
    # Boss status
    alive_b=sum(1 for b in bosses if b.alive)
    bcol=RED if alive_b>0 else GREEN
    surf.blit(font.render(f"Bosses: {alive_b}/{len(bosses)}",True,bcol),(250,12))
    if alive_b==0:
        surf.blit(font.render("PORTAL OPEN!",True,PURPLE),(400,12))
    surf.blit(font.render("[E] Talk  [SPACE] Attack  [R] Dungeon",True,GRAY),(GAME_W-350,12))

def draw_city_panel(surf,font,small_font,player,gold,bosses,equipped,quests_done=None):
    if quests_done is None: quests_done=set()
    px2=GAME_W
    pygame.draw.rect(surf,PANEL_BG,(px2,0,PANEL_W,SCREEN_H))
    pygame.draw.line(surf,(40,40,60),(px2,0),(px2,SCREEN_H),2)
    y=10
    def heading(text,col=WHITE):
        nonlocal y
        t=font.render(text,True,col); surf.blit(t,(px2+8,y)); y+=t.get_height()+4
        pygame.draw.line(surf,(40,40,60),(px2+6,y),(px2+PANEL_W-6,y),1); y+=6
    def line(text,col=GRAY):
        nonlocal y
        t=small_font.render(text,True,col); surf.blit(t,(px2+8,y)); y+=t.get_height()+3
    heading("HAVEN CITY",CYAN)
    line("W A S D  Move",WHITE)
    line("[E] Talk to NPC",WHITE)
    line("[SPACE] Attack boss",WHITE)
    line("[R] Start dungeon",WHITE)
    y+=6
    heading("GOLD",(255,215,0))
    pygame.draw.circle(surf,GOLD_COIN_COLOR,(px2+14,y+5),6)
    surf.blit(font.render(f"{gold}",True,GOLD_COIN_COLOR),(px2+24,y)); y+=18
    heading("HP",(200,80,80))
    surf.blit(small_font.render("HP:",True,WHITE),(px2+8,y))
    for i in range(player.max_hp):
        col=RED if i<int(player.hp+0.99) else (50,20,20)
        hx=px2+38+i*14; hy=y+1
        pygame.draw.rect(surf,col,(hx,hy+2,5,5)); pygame.draw.rect(surf,col,(hx+5,hy+2,5,5))
        pygame.draw.rect(surf,col,(hx+1,hy,9,4)); pygame.draw.rect(surf,col,(hx+2,hy+6,7,3))
    y+=18
    heading("EQUIPMENT",(180,130,200))
    for slot in ["helmet","armor","weapon"]:
        eid=equipped.get(slot)
        if eid:
            for it in SHOP_ITEMS:
                if it["id"]==eid: line(f"{slot}: {it['name']}",it["color"]); break
        else: line(f"{slot}: none",(80,80,80))
    y+=6
    heading("BOSSES",(200,80,80))
    for b in bosses:
        bc=GREEN if not b.alive else RED
        status="DEFEATED" if not b.alive else f"HP {b.hp}/{b.max_hp}"
        line(f"{b.name}: {status}",bc)
    y+=6
    if all(not b.alive for b in bosses):
        heading("FINALE",(155,50,200))
        line("Portal is OPEN!",PURPLE)
        line("Walk to the portal!",WHITE)
        line("3 killers + 6 gens!",RED)
        line("Win = 10000 gold!",GOLD_COIN_COLOR)
    y+=6
    heading("QUESTS",(200,180,80))
    done_ct=len(quests_done); total_ct=len(QUESTS)
    line(f"{done_ct}/{total_ct} complete",GREEN if done_ct==total_ct else WHITE)
    for q in QUESTS:
        if q["id"] not in quests_done:
            line(f"[ ] {q['name']}",GRAY)
            line(f"    {q['desc']}  +{q['gold']}g",(120,120,80))
            break  # Show only next incomplete quest to save space
    if done_ct==total_ct:
        line("ALL DONE!",GREEN)

def draw_dialog(surf,font,small_font,npc_name,text,npc_color):
    bh=80
    pygame.draw.rect(surf,(10,10,20),(0,SCREEN_H-bh,SCREEN_W,bh))
    pygame.draw.line(surf,GRAY,(0,SCREEN_H-bh),(SCREEN_W,SCREEN_H-bh),2)
    surf.blit(font.render(npc_name,True,npc_color),(12,SCREEN_H-bh+8))
    surf.blit(small_font.render(text,True,WHITE),(12,SCREEN_H-bh+30))
    surf.blit(small_font.render("ENTER=next  ESC=close",True,GRAY),(12,SCREEN_H-bh+55))

def apply_equip(player,equipped):
    player.max_hp=MAX_HP; player.speed=4.5
    extra={"stun_range":0,"stun_dur":0,"stun_cd":0}
    player.equip={}
    for slot,item_id in equipped.items():
        for it in SHOP_ITEMS:
            if it["id"]==item_id:
                b=it["bonus"]
                player.max_hp+=b.get("max_hp",0)
                player.speed+=b.get("speed",0)
                extra["stun_range"]+=b.get("stun_range",0)
                extra["stun_dur"]+=b.get("stun_dur",0)
                extra["stun_cd"]+=b.get("stun_cd",0)
                player.equip[slot]=it; break
    player.hp=float(player.max_hp)
    return extra


# â”€â”€ HUD (top bar) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def draw_hud(surf,font,small_font,generators,survivors,player,exit_open,killer,gold=0):
    pygame.draw.rect(surf,(8,8,16),(0,0,GAME_W,HUD_H))
    pygame.draw.line(surf,GRAY,(0,HUD_H),(GAME_W,HUD_H),1)
    done=sum(1 for g in generators if g.done); total=len(generators)

    # Generator progress bar â€” one segment per generator
    bar_x=8; bar_y=8; seg_w=28; seg_h=24; gap=4
    surf.blit(small_font.render("GENS",True,GRAY),(bar_x, bar_y+6))
    bar_x+=38
    for i,g in enumerate(generators):
        bx=bar_x+i*(seg_w+gap)
        if g.done:
            pygame.draw.rect(surf,GREEN,     (bx,bar_y,seg_w,seg_h))
            pygame.draw.rect(surf,(30,160,50),(bx,bar_y,seg_w,seg_h),1)
            # Checkmark
            pygame.draw.line(surf,WHITE,(bx+5,bar_y+13),(bx+11,bar_y+18),2)
            pygame.draw.line(surf,WHITE,(bx+11,bar_y+18),(bx+22,bar_y+7),2)
        elif g.progress>0:
            pygame.draw.rect(surf,(30,30,30),(bx,bar_y,seg_w,seg_h))
            fill_h=int(seg_h*g.progress)
            pygame.draw.rect(surf,YELLOW,(bx,bar_y+seg_h-fill_h,seg_w,fill_h))
            pygame.draw.rect(surf,ORANGE,(bx,bar_y,seg_w,seg_h),1)
        else:
            pygame.draw.rect(surf,(30,30,30),(bx,bar_y,seg_w,seg_h))
            pygame.draw.rect(surf,GRAY,    (bx,bar_y,seg_w,seg_h),1)

    bar_x += total*(seg_w+gap)+10
    alive=sum(1 for s in survivors if s.alive and not s.escaped)
    esc=sum(1 for s in survivors if s.escaped)+(1 if player.escaped else 0)
    surf.blit(font.render(f"Surv {alive}  Out {esc}",True,WHITE),(bar_x,12))
    surf.blit(font.render(f"KILLER: {killer.name}",True,killer.accent),(bar_x+160,12))
    # Gold display
    coin_x=bar_x+330
    pygame.draw.circle(surf,GOLD_COIN_COLOR,(coin_x,20),7)
    pygame.draw.circle(surf,(180,150,0),(coin_x,20),7,1)
    surf.blit(font.render(f"{gold}",True,GOLD_COIN_COLOR),(coin_x+10,12))

    msg="EXIT OPEN â€” RUN!" if exit_open else ""
    if msg: surf.blit(font.render(msg,True,GREEN),(GAME_W-font.size(msg)[0]-8,12))
    if player.slowed_timer>0:
        surf.blit(font.render(f"SLOWED {player.slowed_timer:.1f}s",True,(100,160,255)),(GAME_W-200,12))


# â”€â”€ Side Panel (controls + status) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def draw_panel(surf, font, small_font, player, killer, stun_cd_remaining, survivors, gold=0):
    px2=GAME_W
    pygame.draw.rect(surf,PANEL_BG,(px2,0,PANEL_W,SCREEN_H))
    pygame.draw.line(surf,(40,40,60),(px2,0),(px2,SCREEN_H),2)

    y=10
    def heading(text,col=WHITE):
        nonlocal y
        t=font.render(text,True,col)
        surf.blit(t,(px2+8,y)); y+=t.get_height()+4
        pygame.draw.line(surf,(40,40,60),(px2+6,y),(px2+PANEL_W-6,y),1); y+=6

    def line(text,col=GRAY):
        nonlocal y
        t=small_font.render(text,True,col)
        surf.blit(t,(px2+8,y)); y+=t.get_height()+3

    heading("CONTROLS",(180,180,100))
    line("W A S D",WHITE); line("  Move",GRAY)
    line("ARROWS",WHITE);  line("  Also move",GRAY)
    line("[E]",WHITE);     line("  Repair generator",GRAY)
    line("[SPACE]",WHITE); line("  Stun killer",GRAY)
    line("[R]",WHITE);     line("  Restart round",GRAY)
    line("[ESC]",WHITE);   line("  Quit",GRAY)
    y+=8

    heading("OBJECTIVE",(100,200,100))
    line("Repair all 5 gens",WHITE)
    line("Then reach EXIT",WHITE)
    line("Survivors help you!",GREEN)
    y+=8

    heading("GOLD",(255,215,0))
    pygame.draw.circle(surf,GOLD_COIN_COLOR,(px2+14,y+5),6)
    pygame.draw.circle(surf,(180,150,0),(px2+14,y+5),6,1)
    surf.blit(font.render(f"{gold}",True,GOLD_COIN_COLOR),(px2+24,y))
    y+=16
    line(f"Gen done: +{GOLD_PER_GEN}g",(180,180,100))
    line(f"Escape: +{GOLD_PER_ESCAPE}g",(180,180,100))
    line(f"Stun: +{GOLD_PER_STUN}g",(180,180,100))
    line(f"Surv out: +{GOLD_PER_SURV_ESC}g ea",(180,180,100))
    y+=8

    heading("STATUS",(180,130,200))
    # HP hearts
    surf.blit(small_font.render("HP:",True,WHITE),(px2+8,y))
    for i in range(player.max_hp):
        col=RED if i<int(player.hp+0.99) else (50,20,20)
        hx=px2+38+i*18; hy=y+1
        pygame.draw.rect(surf,col,(hx,hy+2,5,5))
        pygame.draw.rect(surf,col,(hx+5,hy+2,5,5))
        pygame.draw.rect(surf,col,(hx+1,hy,9,4))
        pygame.draw.rect(surf,col,(hx+2,hy+6,7,3))
        pygame.draw.rect(surf,col,(hx+3,hy+8,5,2))
    y+=18

    # Stun cooldown bar
    surf.blit(small_font.render("STUN CD:",True,WHITE),(px2+8,y)); y+=14
    bar_w=PANEL_W-16; cd_frac=stun_cd_remaining/STUN_CD
    ready=stun_cd_remaining<=0
    pygame.draw.rect(surf,(30,30,30),(px2+8,y,bar_w,10))
    bar_col=GREEN if ready else YELLOW
    pygame.draw.rect(surf,bar_col,(px2+8,y,int(bar_w*(1-cd_frac)),10))
    pygame.draw.rect(surf,GRAY,(px2+8,y,bar_w,10),1)
    status="READY!" if ready else f"{stun_cd_remaining:.1f}s"
    surf.blit(small_font.render(status,True,bar_col),(px2+8,y+12)); y+=26

    if player.slowed_timer>0:
        surf.blit(small_font.render(f"SLOWED {player.slowed_timer:.1f}s",True,(100,160,255)),(px2+8,y)); y+=16

    y+=8
    heading("KILLER",(200,80,80))
    line(killer.title,killer.accent)
    for part in killer.ability_label.split(":",1):
        line(part.strip()if part.strip() else "",WHITE)
    if killer.stunned>0:
        surf.blit(font.render("** STUNNED **",True,YELLOW),(px2+6,y)); y+=20
    y+=8

    heading("LEGEND",(130,130,160))
    items=[
        ((50,210,225),"You (cyan)"),
        ((50,200,80), "Mia"),
        ((220,100,180),"Jake"),
        ((155,50,200),"Anya"),
        ((230,130,30),"Omar"),
        (killer.accent, f"{killer.name} (killer)"),
        (ORANGE,       "Generator"),
        (GREEN,        "Exit door"),
    ]
    for col,label in items:
        pygame.draw.rect(surf,col,(px2+8,y+2,10,10))
        surf.blit(small_font.render(label,True,(180,180,180)),(px2+22,y)); y+=14

    # Show respawn timers for dead survivors
    dead=[s for s in survivors if not s.alive and not s.escaped]
    if dead:
        y+=4; heading("RESPAWNING",(200,100,100))
        for s in dead:
            t=math.ceil(s.respawn_timer)
            surf.blit(small_font.render(f"{s.name}: {t}s",True,s.color),(px2+8,y)); y+=14


# â”€â”€ Overlay (win/lose) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def draw_overlay(surf,font,big_font,text,sub,col):
    ov=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
    ov.fill((0,0,0,170)); surf.blit(ov,(0,0))
    t1=big_font.render(text,True,col)
    t2=font.render(sub,True,WHITE)
    t3=font.render("R = restart   ESC = quit",True,GRAY)
    surf.blit(t1,t1.get_rect(center=(SCREEN_W//2,SCREEN_H//2-55)))
    surf.blit(t2,t2.get_rect(center=(SCREEN_W//2,SCREEN_H//2+10)))
    surf.blit(t3,t3.get_rect(center=(SCREEN_W//2,SCREEN_H//2+55)))


# â”€â”€ Killer Reveal â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def draw_reveal(surf,font,big_font,title_font,small_font,klass,timer):
    surf.fill((5,2,8))
    t=pygame.time.get_ticks()/1000.0
    for row in range(0,SCREEN_H,6):
        v=int(14+7*math.sin(row*0.05+t*2))
        pygame.draw.line(surf,(0,0,v),(0,row),(SCREEN_W,row))
    cx,cy=SCREEN_W//2,SCREEN_H//2-20
    gr=int(90+14*math.sin(t*3))
    for r in range(gr,0,-10):
        gs=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
        pygame.draw.circle(gs,(*klass.accent,max(0,int(55*r/gr))),(r,r),r); surf.blit(gs,(cx-r,cy-r))
    # Draw big pixel killer sprite (scaled up 3x)
    tmp=pygame.Surface((64,64),pygame.SRCALPHA); tmp.fill((0,0,0,0))
    draw_killer_sprite(tmp,32,32,klass.name,stunned=False,frame=int(t*30))
    big=pygame.transform.scale(tmp,(192,192))
    surf.blit(big,(cx-96,cy-96))
    warn=title_font.render("YOUR KILLER THIS ROUND:",True,(140,25,25))
    surf.blit(warn,warn.get_rect(center=(SCREEN_W//2,80)))
    surf.blit(title_font.render(klass.name,True,klass.accent),
              title_font.render(klass.name,True,klass.accent).get_rect(center=(SCREEN_W//2,150)))
    surf.blit(big_font.render(klass.title,True,WHITE),
              big_font.render(klass.title,True,WHITE).get_rect(center=(SCREEN_W//2,210)))
    for i,ln in enumerate(klass.description.split('\n')):
        t2=font.render(ln,True,(185,185,185)); surf.blit(t2,t2.get_rect(center=(SCREEN_W//2,SCREEN_H-200+i*26)))
    ab=font.render(klass.ability_label,True,klass.accent); surf.blit(ab,ab.get_rect(center=(SCREEN_W//2,SCREEN_H-148)))
    bw=320; bx=SCREEN_W//2-bw//2; by=SCREEN_H-92
    pygame.draw.rect(surf,GRAY,(bx,by,bw,14),border_radius=7)
    pygame.draw.rect(surf,klass.accent,(bx,by,int(bw*timer/REVEAL_DUR),14),border_radius=7)
    surf.blit(small_font.render(f"Starting in {timer:.1f}s  â€”  ENTER to skip",True,GRAY),
              small_font.render(f"Starting in {timer:.1f}s  â€”  ENTER to skip",True,GRAY).get_rect(center=(SCREEN_W//2,SCREEN_H-62)))


# â”€â”€ New Game â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def new_game(old_gens=None, old_grid=None, old_rooms=None, old_ep=None):
    # If we have old data (restart after death), reuse the map and keep gen progress
    if old_grid is not None and old_rooms is not None:
        grid=old_grid; rooms=old_rooms; floors=floor_tiles(grid)
        random.shuffle(rooms); used=[]
        def pick():
            for r in rooms:
                c=room_center(r)
                if c not in used: used.append(c); return c
            return random.choice(floors)
        ps=pick(); ks=pick()
        # Reuse generators â€” keep their progress!
        gens=old_gens
        ep=old_ep
        # Mark used positions for gens and exit
        for g in gens: used.append((g.tx,g.ty))
        used.append(ep)
        survs=[Survivor(*pick(),n,c) for n,c in [("Mia",GREEN),("Jake",PINK),("Anya",PURPLE),("Omar",ORANGE)]]
        player=Player(*ps)
        KC=random.choice(ALL_KILLERS); killer=KC(*ks)
        return grid,gens,survs,player,killer,ep,KC,rooms
    else:
        grid,rooms=generate_map(); floors=floor_tiles(grid); random.shuffle(rooms); used=[]
        def pick():
            for r in rooms:
                c=room_center(r)
                if c not in used: used.append(c); return c
            return random.choice(floors)
        ps=pick(); ks=pick()
        gens=[Generator(*pick()) for _ in range(5)]
        ep=pick()
        survs=[Survivor(*pick(),n,c) for n,c in [("Mia",GREEN),("Jake",PINK),("Anya",PURPLE),("Omar",ORANGE)]]
        player=Player(*ps)
        KC=random.choice(ALL_KILLERS); killer=KC(*ks)
        return grid,gens,survs,player,killer,ep,KC,rooms


def new_finale():
    grid,rooms=generate_map(); floors=floor_tiles(grid); random.shuffle(rooms); used=[]
    def pick():
        for r in rooms:
            c=room_center(r)
            if c not in used: used.append(c); return c
        return random.choice(floors)
    ps=pick()
    kcs=random.sample(ALL_KILLERS,3)
    killers2=[KC(*pick()) for KC in kcs]
    gens=[Generator(*pick()) for _ in range(6)]
    ep=pick()
    survs=[Survivor(*pick(),n,c) for n,c in [("Mia",GREEN),("Jake",PINK),("Anya",PURPLE),("Omar",ORANGE)]]
    return grid,gens,survs,ps,killers2,ep,rooms


# â”€â”€ Main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async def main():
    pygame.init()
    screen=pygame.display.set_mode((SCREEN_W,SCREEN_H))
    pygame.display.set_caption("DOOMSDAY RACE")
    clock=pygame.time.Clock()
    font=pygame.font.SysFont("consolas",15,bold=True)
    small_font=pygame.font.SysFont("consolas",11)
    big_font=pygame.font.SysFont("consolas",44,bold=True)
    title_font=pygame.font.SysFont("consolas",54,bold=True)

    state=STATE_MENU
    grid=gens=survs=player=killer=ep=KC=None
    rooms=None; reveal_timer=REVEAL_DUR
    gold=0; gold_popup=[]; gens_rewarded=set()
    # City persistent state
    city_grid=generate_city()
    city_npcs=[CityNPC(d) for d in CITY_NPC_DEFS]
    city_bosses=[CityBoss(d) for d in BOSS_DEFS]
    cam_x=0.0; cam_y=0.0
    owned_items=set(); equipped={}; shop_cursor=0
    dialog_active=False; dialog_npc=None; dialog_lines=[]; dialog_idx=0
    equip_extra={"stun_range":0,"stun_dur":0,"stun_cd":0}
    # Food shop state
    food_menu=[]; food_cursor=0; active_shop_name=""
    # Quest tracking
    quests_done=set()
    # Finale state
    finale_killers=[]; finale_mode=False

    def enter_city():
        nonlocal state,player,cam_x,cam_y
        state=STATE_CITY
        player=Player(40,25)  # plaza, north of fountain
        equip_extra.update(apply_equip(player,equipped))
        cam_x=player.tx-COLS//2; cam_y=player.ty-ROWS//2

    def start_dungeon(keep_progress=False):
        nonlocal grid,gens,survs,player,killer,ep,KC,rooms,state,reveal_timer,gens_rewarded,finale_mode,equip_extra
        finale_mode=False
        if keep_progress and grid is not None:
            grid,gens,survs,player,killer,ep,KC,rooms=new_game(gens,grid,rooms,ep)
        else:
            grid,gens,survs,player,killer,ep,KC,rooms=new_game()
            gens_rewarded=set()
        equip_extra.update(apply_equip(player,equipped))
        reveal_timer=REVEAL_DUR; state=STATE_REVEAL

    def start_finale():
        nonlocal grid,gens,survs,player,finale_killers,ep,rooms,state,reveal_timer,gens_rewarded,finale_mode,equip_extra,killer,KC
        finale_mode=True
        grid,gens,survs,ps,finale_killers,ep,rooms=new_finale()
        gens_rewarded=set()
        player=Player(*ps)
        equip_extra.update(apply_equip(player,equipped))
        killer=finale_killers[0]; KC=type(killer)  # for reveal screen
        reveal_timer=REVEAL_DUR; state=STATE_FINALE_REVEAL

    while True:
        dt=min(clock.tick(FPS)/1000.0,0.05)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    if state==STATE_SHOP:
                        state=STATE_CITY; continue
                    elif state==STATE_FOOD_SHOP:
                        state=STATE_CITY; continue
                    elif dialog_active:
                        dialog_active=False; continue
                    else: pygame.quit(); sys.exit()
                if event.key==pygame.K_RETURN:
                    if state==STATE_FOOD_SHOP:
                        if food_menu and 0<=food_cursor<len(food_menu):
                            item=food_menu[food_cursor]
                            if gold>=item["cost"]:
                                gold-=item["cost"]
                                h=item.get("heal",0)
                                if h>0: player.hp=min(player.max_hp,player.hp+h)
                                buff=item.get("buff",None)
                                if buff=="speed": player.speed+=0.3
                                elif buff=="shield": player.max_hp+=1; player.hp+=1
                                elif buff=="stun": equip_extra["stun_cd"]-=0.5
                        continue
                    if dialog_active:
                        dialog_idx+=1
                        if dialog_idx>=len(dialog_lines):
                            dialog_active=False
                            if dialog_npc and dialog_npc.is_shop:
                                if dialog_npc.shop_type=="gear":
                                    state=STATE_SHOP; shop_cursor=0
                                elif dialog_npc.shop_type in ("food","potion","pet","inn","scroll","chef"):
                                    food_menu=get_food_menu(dialog_npc.shop_type)
                                    food_cursor=0; active_shop_name=dialog_npc.name
                                    state=STATE_FOOD_SHOP
                        continue
                    if state==STATE_MENU: start_dungeon()
                    elif state==STATE_REVEAL: state=STATE_PLAYING
                    elif state==STATE_FINALE_REVEAL: state=STATE_FINALE
                    elif state==STATE_WIN: enter_city()
                    elif state==STATE_FINALE_WIN: enter_city()
                    elif state==STATE_SHOP:
                        item=SHOP_ITEMS[shop_cursor]
                        if item["id"] in owned_items:
                            equipped[item["slot"]]=item["id"]
                            player.equip={};
                            for sl,eid in equipped.items():
                                for it2 in SHOP_ITEMS:
                                    if it2["id"]==eid: player.equip[sl]=it2; break
                        elif gold>=item["cost"]:
                            gold-=item["cost"]; owned_items.add(item["id"])
                            equipped[item["slot"]]=item["id"]
                            player.equip={};
                            for sl,eid in equipped.items():
                                for it2 in SHOP_ITEMS:
                                    if it2["id"]==eid: player.equip[sl]=it2; break
                            # Gear buy quest
                            for q in QUESTS:
                                if q["type"]=="buy" and q["target"]=="gear" and q["id"] not in quests_done:
                                    quests_done.add(q["id"]); gold+=q["gold"]
                                    gold_popup.append((f'+{q["gold"]}g Quest!',SCREEN_W//2,100,2.0))
                    elif state==STATE_FOOD_SHOP:
                        pass  # handled at top of ENTER block
                if event.key==pygame.K_r:
                    if state==STATE_LOSE:
                        if finale_mode: start_finale()
                        else: start_dungeon(keep_progress=True)
                    elif state in(STATE_WIN,STATE_PLAYING): start_dungeon(keep_progress=False)
                    elif state==STATE_CITY: start_dungeon(keep_progress=False)
                if state==STATE_SHOP:
                    if event.key in(pygame.K_UP,pygame.K_w): shop_cursor=(shop_cursor-2)%len(SHOP_ITEMS)
                    elif event.key in(pygame.K_DOWN,pygame.K_s): shop_cursor=(shop_cursor+2)%len(SHOP_ITEMS)
                    elif event.key in(pygame.K_LEFT,pygame.K_a): shop_cursor=(shop_cursor-1)%len(SHOP_ITEMS)
                    elif event.key in(pygame.K_RIGHT,pygame.K_d): shop_cursor=(shop_cursor+1)%len(SHOP_ITEMS)
                if state==STATE_FOOD_SHOP and food_menu:
                    if event.key in(pygame.K_UP,pygame.K_w): food_cursor=(food_cursor-1)%len(food_menu)
                    elif event.key in(pygame.K_DOWN,pygame.K_s): food_cursor=(food_cursor+1)%len(food_menu)
                if event.key==pygame.K_SPACE:
                    if state==STATE_PLAYING and not finale_mode:
                        if player.alive and not player.escaped and player.stun_cd<=0:
                            sr=STUN_RANGE+equip_extra["stun_range"]
                            if math.dist((player.tx,player.ty),(killer.tx,killer.ty))<sr:
                                killer.stunned=STUN_DUR+equip_extra["stun_dur"]
                                player.stun_cd=max(1.0,STUN_CD+equip_extra["stun_cd"])
                                gold+=GOLD_PER_STUN
                                gpx=int(player.tx*TILE+TILE//2); gpy=int(player.ty*TILE+TILE//2+HUD_H)
                                gold_popup.append((f"+{GOLD_PER_STUN}g",gpx,gpy-40,1.5))
                    elif state==STATE_FINALE:
                        if player.alive and not player.escaped and player.stun_cd<=0:
                            sr=STUN_RANGE+equip_extra["stun_range"]
                            for fk in finale_killers:
                                if fk.stunned<=0 and math.dist((player.tx,player.ty),(fk.tx,fk.ty))<sr:
                                    fk.stunned=STUN_DUR+equip_extra["stun_dur"]
                                    player.stun_cd=max(1.0,STUN_CD+equip_extra["stun_cd"])
                                    gold+=GOLD_PER_STUN; break
                    elif state==STATE_CITY:
                        if player.alive and player.stun_cd<=0:
                            for boss in city_bosses:
                                if boss.alive and math.dist((player.tx,player.ty),(boss.tx,boss.ty))<2.0:
                                    killed=boss.take_damage(); player.stun_cd=0.8
                                    if killed and not boss.rewarded:
                                        boss.rewarded=True; gold+=boss.gold_reward
                                        gold_popup.append((f"+{boss.gold_reward}g",int((boss.tx-cam_x)*TILE+TILE//2),int((boss.ty-cam_y)*TILE+TILE//2+HUD_H)-20,2.0))
                                    break
                if event.key==pygame.K_e and state==STATE_CITY and not dialog_active:
                    for npc in city_npcs:
                        if math.dist((player.tx,player.ty),(npc.tx,npc.ty))<3.5:
                            dialog_active=True; dialog_npc=npc
                            dialog_lines=npc.dialog; dialog_idx=0
                            if npc.heals: player.hp=float(player.max_hp)
                            # Talk quests
                            for q in QUESTS:
                                if q["type"]=="talk" and q["target"]==npc.name and q["id"] not in quests_done:
                                    quests_done.add(q["id"]); gold+=q["gold"]
                                    gold_popup.append((f'+{q["gold"]}g Quest!',int((player.tx-cam_x)*TILE+TILE//2),int((player.ty-cam_y)*TILE+HUD_H)-30,2.0))
                            break

        # â•â•â• STATE UPDATES â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        # MENU
        if state==STATE_MENU:
            screen.fill(DARK_GRAY)
            screen.blit(title_font.render("DOOMSDAY",True,RED),
                        title_font.render("DOOMSDAY",True,RED).get_rect(center=(SCREEN_W//2,180)))
            screen.blit(title_font.render("RACE",True,ORANGE),
                        title_font.render("RACE",True,ORANGE).get_rect(center=(SCREEN_W//2,248)))
            screen.blit(font.render("Repair generators. Survive. Escape.",True,WHITE),
                        font.render("Repair generators. Survive. Escape.",True,WHITE).get_rect(center=(SCREEN_W//2,360)))
            screen.blit(font.render("Press ENTER to start",True,CYAN),
                        font.render("Press ENTER to start",True,CYAN).get_rect(center=(SCREEN_W//2,410)))
            screen.blit(small_font.render("5 killer skins | Shop | City | Bosses | 3-Killer Finale!",True,(160,80,80)),
                        small_font.render("5 killer skins | Shop | City | Bosses | 3-Killer Finale!",True,(160,80,80)).get_rect(center=(SCREEN_W//2,460)))
            await asyncio.sleep(0); pygame.display.flip(); continue

        # REVEAL (dungeon)
        if state==STATE_REVEAL:
            reveal_timer-=dt
            if reveal_timer<=0: state=STATE_PLAYING
            draw_reveal(screen,font,big_font,title_font,small_font,KC,max(0,reveal_timer))
            await asyncio.sleep(0); pygame.display.flip(); continue

        # FINALE REVEAL
        if state==STATE_FINALE_REVEAL:
            reveal_timer-=dt
            if reveal_timer<=0: state=STATE_FINALE
            screen.fill((5,2,8))
            t=pygame.time.get_ticks()/1000.0
            warn=title_font.render("THE FINALE!",True,RED)
            screen.blit(warn,warn.get_rect(center=(SCREEN_W//2,60)))
            screen.blit(big_font.render("3 KILLERS  |  6 GENERATORS  |  1 EXIT",True,ORANGE),
                        big_font.render("3 KILLERS  |  6 GENERATORS  |  1 EXIT",True,ORANGE).get_rect(center=(SCREEN_W//2,140)))
            # Draw all 3 killer sprites
            for i,fk in enumerate(finale_killers):
                tmp=pygame.Surface((64,64),pygame.SRCALPHA); tmp.fill((0,0,0,0))
                draw_killer_sprite(tmp,32,32,fk.name,frame=int(t*30))
                big2=pygame.transform.scale(tmp,(128,128))
                sx=SCREEN_W//2-200+i*200
                screen.blit(big2,(sx-64,220))
                screen.blit(font.render(fk.name,True,fk.accent),
                            font.render(fk.name,True,fk.accent).get_rect(center=(sx,370)))
            screen.blit(font.render(f"Win = {GOLD_FINALE_WIN} GOLD!",True,GOLD_COIN_COLOR),
                        font.render(f"Win = {GOLD_FINALE_WIN} GOLD!",True,GOLD_COIN_COLOR).get_rect(center=(SCREEN_W//2,420)))
            bar_w=320; bx=SCREEN_W//2-bar_w//2; by=SCREEN_H-92
            pygame.draw.rect(screen,GRAY,(bx,by,bar_w,14),border_radius=7)
            pygame.draw.rect(screen,RED,(bx,by,int(bar_w*reveal_timer/REVEAL_DUR),14),border_radius=7)
            screen.blit(small_font.render(f"Starting in {reveal_timer:.1f}s  â€” ENTER to skip",True,GRAY),
                        small_font.render(f"Starting in {reveal_timer:.1f}s  â€” ENTER to skip",True,GRAY).get_rect(center=(SCREEN_W//2,SCREEN_H-62)))
            await asyncio.sleep(0); pygame.display.flip(); continue

        # PLAYING (dungeon - single killer)
        if state==STATE_PLAYING:
            keys=pygame.key.get_pressed()
            exit_open=all(g.done for g in gens)
            for g in gens: g.active=False
            player.update(dt,grid,keys,gens,exit_open,ep)
            killer.update(dt,grid,survs,player)
            killer_tiles=[killer.tile]
            for s in survs: s.update(dt,grid,gens,exit_open,ep,killer_tiles,player)
            for g in gens: g.update(dt)
            for i,g in enumerate(gens):
                if g.done and i not in gens_rewarded:
                    gens_rewarded.add(i); gold+=GOLD_PER_GEN
                    gpx=int(g.tx*TILE+TILE//2); gpy=int(g.ty*TILE+TILE//2+HUD_H)
                    gold_popup.append((f"+{GOLD_PER_GEN}g",gpx,gpy-20,2.0))
            if not player.alive: state=STATE_LOSE
            elif player.escaped:
                gold+=GOLD_PER_ESCAPE
                gold+=sum(1 for s in survs if s.escaped)*GOLD_PER_SURV_ESC
                state=STATE_WIN

        # FINALE (3 killers)
        if state==STATE_FINALE:
            keys=pygame.key.get_pressed()
            exit_open=all(g.done for g in gens)
            for g in gens: g.active=False
            player.update(dt,grid,keys,gens,exit_open,ep)
            killer_tiles=[]
            for fk in finale_killers:
                fk.update(dt,grid,survs,player); killer_tiles.append(fk.tile)
            for s in survs: s.update(dt,grid,gens,exit_open,ep,killer_tiles,player)
            for g in gens: g.update(dt)
            for i,g in enumerate(gens):
                if g.done and i not in gens_rewarded:
                    gens_rewarded.add(i); gold+=GOLD_PER_GEN
                    gpx=int(g.tx*TILE+TILE//2); gpy=int(g.ty*TILE+TILE//2+HUD_H)
                    gold_popup.append((f"+{GOLD_PER_GEN}g",gpx,gpy-20,2.0))
            if not player.alive: state=STATE_LOSE
            elif player.escaped:
                gold+=GOLD_FINALE_WIN; state=STATE_FINALE_WIN

        # CITY
        if state==STATE_CITY and not dialog_active:
            keys=pygame.key.get_pressed()
            player.update_city(dt,city_grid,keys,CITY_W,CITY_H)
            cam_x=max(0,min(CITY_W-COLS,player.tx-COLS//2))
            cam_y=max(0,min(CITY_H-ROWS,player.ty-ROWS//2))
            for boss in city_bosses: boss.update(dt,city_grid,player)
            for npc in city_npcs: npc.update(dt,city_grid)
            # Healer auto-heal
            for npc in city_npcs:
                if npc.heals and math.dist((player.tx,player.ty),(npc.tx,npc.ty))<2.5:
                    player.hp=min(player.max_hp,player.hp+2*dt)
            # Lava damage
            ptx,pty=int(player.tx),int(player.ty)
            if 0<=pty<CITY_H and 0<=ptx<CITY_W and city_grid[pty][ptx]==C_LAVA:
                player.take_hit()
            # Quest zone checks
            if 0<=pty<15 and 0<=ptx<18 and "explore_desert" not in quests_done: quests_done.add("explore_desert"); gold+=40; gold_popup.append(("+40g Quest!",int((player.tx-cam_x)*TILE+TILE//2),int((player.ty-cam_y)*TILE+HUD_H)-30,2.0))
            if 9<=pty<20 and 60<=ptx<CITY_W and "explore_snow" not in quests_done: quests_done.add("explore_snow"); gold+=40; gold_popup.append(("+40g Quest!",int((player.tx-cam_x)*TILE+TILE//2),int((player.ty-cam_y)*TILE+HUD_H)-30,2.0))
            if 35<=pty and 0<=ptx<18 and "explore_mushroom" not in quests_done: quests_done.add("explore_mushroom"); gold+=40; gold_popup.append(("+40g Quest!",int((player.tx-cam_x)*TILE+TILE//2),int((player.ty-cam_y)*TILE+HUD_H)-30,2.0))
            if 35<=pty and 60<=ptx and "explore_swamp" not in quests_done: quests_done.add("explore_swamp"); gold+=40; gold_popup.append(("+40g Quest!",int((player.tx-cam_x)*TILE+TILE//2),int((player.ty-cam_y)*TILE+HUD_H)-30,2.0))
            if 70<=player.tx<=80 and 0<=player.ty<=8 and "visit_house" not in quests_done: quests_done.add("visit_house"); gold+=100; gold_popup.append(("+100g Quest!",int((player.tx-cam_x)*TILE+TILE//2),int((player.ty-cam_y)*TILE+HUD_H)-30,2.0))
            # Kill quest checks
            for b in city_bosses:
                if not b.alive:
                    qid="kill_"+b.name.lower().replace(" ","_")
                    # Match by boss name
                    for q in QUESTS:
                        if q["type"]=="kill" and q["target"]==b.name and q["id"] not in quests_done:
                            quests_done.add(q["id"]); gold+=q["gold"]
                            gold_popup.append((f'+{q["gold"]}g Quest!',int((player.tx-cam_x)*TILE+TILE//2),int((player.ty-cam_y)*TILE+HUD_H)-30,2.0))
            if all(not b2.alive for b2 in city_bosses) and "kill_all" not in quests_done:
                quests_done.add("kill_all"); gold+=500
                gold_popup.append(("+500g Champion!",int((player.tx-cam_x)*TILE+TILE//2),int((player.ty-cam_y)*TILE+HUD_H)-50,3.0))
            # Safe zone: Your house (71-79, 2-6) â€” fast heal + no boss aggro
            in_house=71<=player.tx<=79 and 2<=player.ty<=6
            if in_house:
                player.hp=min(player.max_hp,player.hp+4*dt)
                for boss in city_bosses: boss.aggro=False
            # Respawn in city if killed by boss
            if not player.alive or player.hp<=0:
                player.alive=True; player.hp=float(player.max_hp)
                player.tx=40.0; player.ty=25.0; player.hit_timer=2.0
                player.flash_timer=1.0
            # Portal check
            ppx,ppy=PORTAL_POS
            if all(not b.alive for b in city_bosses) and math.dist((player.tx,player.ty),(ppx,ppy))<2.0:
                start_finale()
                continue

        # â•â•â• DRAWING â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        screen.fill(DARK_GRAY)

        # SHOP
        if state==STATE_SHOP:
            draw_shop(screen,font,big_font,small_font,gold,owned_items,equipped,shop_cursor,player.equip)
            await asyncio.sleep(0); pygame.display.flip(); continue

        # FOOD SHOP
        if state==STATE_FOOD_SHOP:
            draw_food_shop(screen,font,big_font,small_font,gold,food_menu,food_cursor,active_shop_name)
            await asyncio.sleep(0); pygame.display.flip(); continue

        # CITY DRAW
        if state==STATE_CITY:
            for r in range(max(0,int(cam_y)),min(CITY_H,int(cam_y)+ROWS+2)):
                for c in range(max(0,int(cam_x)),min(CITY_W,int(cam_x)+COLS+2)):
                    sx=int((c-cam_x)*TILE); sy=int((r-cam_y)*TILE+HUD_H)
                    tile=city_grid[r][c]; col=CITY_COLORS.get(tile,(40,85,35))
                    pygame.draw.rect(screen,col,(sx,sy,TILE,TILE))
                    if tile==C_PATH:
                        pygame.draw.line(screen,(140,125,95),(sx,sy),(sx+TILE,sy))
                        pygame.draw.line(screen,(140,125,95),(sx,sy),(sx,sy+TILE))
                    elif tile==C_BWALL:
                        pygame.draw.rect(screen,(110,85,55),(sx,sy,TILE,4))
                        pygame.draw.rect(screen,(70,55,35),(sx,sy,TILE,TILE),1)
                    elif tile==C_WATER:
                        tw=pygame.time.get_ticks()/500+r*0.3+c*0.2
                        wv=int(10*math.sin(tw))
                        pygame.draw.rect(screen,(max(0,40+wv),max(0,80+wv),min(255,170+wv)),(sx,sy,TILE,TILE))
                    elif tile==C_BED:
                        pygame.draw.rect(screen,(120,100,70),(sx,sy,TILE,TILE))
                        pygame.draw.rect(screen,(140,50,50),(sx+4,sy+4,TILE-8,TILE-8))
                        pygame.draw.rect(screen,(180,70,70),(sx+4,sy+4,TILE-8,8))
                        pygame.draw.rect(screen,(200,180,160),(sx+6,sy+4,10,6))
                    elif tile==C_SAND:
                        pygame.draw.rect(screen,(210,190,130),(sx,sy,TILE,TILE))
                        if (r+c)%5==0: pygame.draw.circle(screen,(190,170,110),(sx+16,sy+16),2)
                    elif tile==C_SNOW:
                        pygame.draw.rect(screen,(220,225,235),(sx,sy,TILE,TILE))
                        if (r*3+c)%7==0: pygame.draw.circle(screen,(240,245,255),(sx+10,sy+12),3)
                        if (r+c*2)%9==0: pygame.draw.circle(screen,(200,210,230),(sx+22,sy+8),2)
                    elif tile==C_LAVA:
                        tw=pygame.time.get_ticks()/300+r+c
                        lv=int(30*math.sin(tw))
                        pygame.draw.rect(screen,(min(255,180+lv),max(0,50+lv//2),20),(sx,sy,TILE,TILE))
                        pygame.draw.rect(screen,(255,160,30),(sx+8,sy+8,16,16))
                    elif tile==C_MUSHROOM:
                        pygame.draw.rect(screen,(70,40,80),(sx,sy,TILE,TILE))
                        if (r+c)%4==0:
                            pygame.draw.circle(screen,(180,60,120),(sx+16,sy+20),5)
                            pygame.draw.rect(screen,(140,120,80),(sx+14,sy+24,4,8))
                        if (r*2+c)%6==0:
                            pygame.draw.circle(screen,(60,200,180),(sx+8,sy+14),3)
                    elif tile==C_SWAMP:
                        pygame.draw.rect(screen,(50,70,35),(sx,sy,TILE,TILE))
                        tw=pygame.time.get_ticks()/600+r*0.2
                        if (r+c)%3==0:
                            bub=int(2+math.sin(tw+c)*2)
                            pygame.draw.circle(screen,(70,100,50),(sx+16,sy+16),bub)
                    elif tile==C_DARKGRASS:
                        pygame.draw.rect(screen,(25,55,20),(sx,sy,TILE,TILE))
                        if (r+c)%4==0: pygame.draw.line(screen,(35,70,30),(sx+8,sy+TILE),(sx+12,sy+10),1)
            # Your House label + safe zone glow
            hsx=int((73-cam_x)*TILE); hsy=int((0-cam_y)*TILE+HUD_H)
            if -100<hsx<GAME_W+100 and -20<hsy<SCREEN_H:
                lbl2=font.render("MY HOUSE",True,(255,220,100))
                screen.blit(lbl2,(hsx,hsy-4))
            for hr in range(2,7):
                for hc in range(71,79):
                    hsx2=int((hc-cam_x)*TILE); hsy2=int((hr-cam_y)*TILE+HUD_H)
                    if 0<hsx2<GAME_W and HUD_H<hsy2<SCREEN_H:
                        gs4=pygame.Surface((TILE,TILE),pygame.SRCALPHA)
                        gs4.fill((80,200,120,20))
                        screen.blit(gs4,(hsx2,hsy2))
            # Portal
            if all(not b.alive for b in city_bosses):
                ppx,ppy=PORTAL_POS
                psx=int((ppx-cam_x)*TILE); psy=int((ppy-cam_y)*TILE+HUD_H)
                tw=pygame.time.get_ticks()/300
                pr=int(14+4*math.sin(tw))
                gs3=pygame.Surface((pr*2,pr*2),pygame.SRCALPHA)
                pygame.draw.circle(gs3,(130,50,200,180),(pr,pr),pr)
                screen.blit(gs3,(psx+TILE//2-pr,psy+TILE//2-pr))
                lbl=small_font.render("PORTAL",True,PURPLE)
                screen.blit(lbl,(psx+TILE//2-lbl.get_width()//2,psy-6))
            draw_city_arrows(screen,cam_x,cam_y,small_font)
            for npc in city_npcs: npc.draw(screen,cam_x,cam_y,small_font)
            for boss in city_bosses: boss.draw(screen,cam_x,cam_y,font,small_font)
            player.draw_city(screen,cam_x,cam_y)
            draw_city_hud(screen,font,small_font,gold,player,city_bosses)
            draw_city_panel(screen,font,small_font,player,gold,city_bosses,equipped,quests_done)
            # Gold popups
            new_popups=[]
            for txt,fpx,fpy,ft in gold_popup:
                ft-=dt; fpy-=40*dt
                if ft>0:
                    gs2=font.render(txt,True,GOLD_COIN_COLOR)
                    screen.blit(gs2,(fpx-gs2.get_width()//2,int(fpy)))
                    new_popups.append((txt,fpx,fpy,ft))
            gold_popup[:]=new_popups
            if dialog_active and dialog_npc:
                txt=dialog_lines[min(dialog_idx,len(dialog_lines)-1)]
                draw_dialog(screen,font,small_font,dialog_npc.name,txt,dialog_npc.color)
            await asyncio.sleep(0); pygame.display.flip(); continue

        # DUNGEON / FINALE DRAW
        if state in(STATE_PLAYING,STATE_WIN,STATE_LOSE,STATE_FINALE,STATE_FINALE_WIN):
            for r in range(ROWS):
                for c in range(COLS):
                    rx=c*TILE; ry=r*TILE+HUD_H
                    if grid[r][c]==FLOOR:
                        pygame.draw.rect(screen,FLOOR_CLR,(rx,ry,TILE,TILE))
                        pygame.draw.line(screen,(25,25,38),(rx,ry),(rx+TILE,ry))
                        pygame.draw.line(screen,(25,25,38),(rx,ry),(rx,ry+TILE))
                    else:
                        pygame.draw.rect(screen,WALL_CLR,(rx,ry,TILE,TILE))
                        pygame.draw.rect(screen,WALL_TOP,(rx,ry,TILE,4))
                        pygame.draw.rect(screen,(25,25,42),(rx,ry,TILE,TILE),1)
            ex,ey=ep
            exit_open=all(g.done for g in gens) if gens else False
            ecol=GREEN if exit_open else DARK_GREEN
            pygame.draw.rect(screen,ecol,(ex*TILE+3,ey*TILE+3+HUD_H,TILE-6,TILE-6))
            pygame.draw.rect(screen,WHITE,(ex*TILE+3,ey*TILE+3+HUD_H,TILE-6,TILE-6),1)
            if exit_open:
                lbl=small_font.render("EXIT",True,BLACK)
                screen.blit(lbl,(ex*TILE+5,ey*TILE+9+HUD_H))
            for g in gens: g.draw(screen)
            for s in survs: s.draw(screen,small_font)
            if finale_mode:
                for fk in finale_killers: fk.draw(screen)
            else:
                if killer: killer.draw(screen)
            player.draw(screen)
            if finale_mode:
                # Finale HUD
                pygame.draw.rect(screen,(8,8,16),(0,0,GAME_W,HUD_H))
                pygame.draw.line(screen,GRAY,(0,HUD_H),(GAME_W,HUD_H),1)
                surf=screen
                bx=8; by2=8; sw2=28; sh2=24; gap2=4
                surf.blit(small_font.render("GENS",True,GRAY),(bx,by2+6)); bx+=38
                for i,g in enumerate(gens):
                    gx=bx+i*(sw2+gap2)
                    if g.done:
                        pygame.draw.rect(surf,GREEN,(gx,by2,sw2,sh2))
                        pygame.draw.line(surf,WHITE,(gx+5,by2+13),(gx+11,by2+18),2)
                        pygame.draw.line(surf,WHITE,(gx+11,by2+18),(gx+22,by2+7),2)
                    elif g.progress>0:
                        pygame.draw.rect(surf,(30,30,30),(gx,by2,sw2,sh2))
                        fh=int(sh2*g.progress)
                        pygame.draw.rect(surf,YELLOW,(gx,by2+sh2-fh,sw2,fh))
                        pygame.draw.rect(surf,ORANGE,(gx,by2,sw2,sh2),1)
                    else:
                        pygame.draw.rect(surf,(30,30,30),(gx,by2,sw2,sh2))
                        pygame.draw.rect(surf,GRAY,(gx,by2,sw2,sh2),1)
                surf.blit(font.render("FINALE!",True,RED),(bx+len(gens)*(sw2+gap2)+10,12))
                # Gold in HUD
                cx3=bx+len(gens)*(sw2+gap2)+100
                pygame.draw.circle(surf,GOLD_COIN_COLOR,(cx3,20),7)
                surf.blit(font.render(f"{gold}",True,GOLD_COIN_COLOR),(cx3+10,12))
                if exit_open: surf.blit(font.render("EXIT OPEN!",True,GREEN),(GAME_W-130,12))
                # Finale panel
                px3=GAME_W
                pygame.draw.rect(screen,PANEL_BG,(px3,0,PANEL_W,SCREEN_H))
                pygame.draw.line(screen,(40,40,60),(px3,0),(px3,SCREEN_H),2)
                py3=10
                screen.blit(font.render("THE FINALE",True,RED),(px3+8,py3)); py3+=24
                for fk in finale_killers:
                    screen.blit(small_font.render(fk.name,True,fk.accent),(px3+8,py3)); py3+=14
                    if fk.stunned>0: screen.blit(small_font.render("STUNNED!",True,YELLOW),(px3+8,py3)); py3+=14
                py3+=8
                screen.blit(font.render("6 Gens + 1 Exit",True,ORANGE),(px3+8,py3)); py3+=20
                screen.blit(font.render(f"Win = {GOLD_FINALE_WIN}g",True,GOLD_COIN_COLOR),(px3+8,py3)); py3+=20
                screen.blit(font.render("SPACE = Stun",True,WHITE),(px3+8,py3)); py3+=16
                screen.blit(font.render("WASD = Move",True,WHITE),(px3+8,py3)); py3+=16
                screen.blit(font.render("E = Repair gen",True,WHITE),(px3+8,py3))
            else:
                draw_hud(screen,font,small_font,gens,survs,player,exit_open,killer,gold)
                draw_panel(screen,font,small_font,player,killer,player.stun_cd,survs,gold)
            # Gold popups
            new_popups=[]
            for txt,fpx,fpy,ft in gold_popup:
                ft-=dt; fpy-=40*dt
                if ft>0:
                    gs2=font.render(txt,True,GOLD_COIN_COLOR)
                    screen.blit(gs2,(fpx-gs2.get_width()//2,int(fpy)))
                    new_popups.append((txt,fpx,fpy,ft))
            gold_popup[:]=new_popups

        if state==STATE_WIN:
            esc=sum(1 for s in survs if s.escaped)
            draw_overlay(screen,font,big_font,"YOU ESCAPED!",f"{esc} also escaped. Gold: {gold}g  ENTER=City",GREEN)
        elif state==STATE_LOSE:
            if finale_mode:
                draw_overlay(screen,font,big_font,"DEFEATED!","The killers were too strong. R=retry  Gold: "+str(gold)+"g",RED)
            else:
                draw_overlay(screen,font,big_font,"YOU WERE CAUGHT!",f"{killer.title} claims another victim. R=retry (gens kept!) Gold: {gold}g",RED)
        elif state==STATE_FINALE_WIN:
            draw_overlay(screen,font,big_font,"YOU WON THE FINALE!",f"+{GOLD_FINALE_WIN} GOLD! Total: {gold}g  You can live in the city!  ENTER=City",GOLD_COIN_COLOR)

        await asyncio.sleep(0)
        pygame.display.flip()

if __name__=="__main__":
    asyncio.run(main())
    
