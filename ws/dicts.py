# -*- coding: utf-8 -*-
"""Словари соответствий (из рабочих скриптов поставок 09.10 и 28.10)."""
CAND={'BLACK':['черный'],'WHITE':['белый'],'WHITE PRINT':['белый'],'IVORY':['айвори','молочный','бежевый'],'PINK':['розовый'],'TAN':['бежевый','светло-коричневый'],'SAND':['песочный','бежевый'],'GREEN':['зеленый'],'BOTTLE':['темно-зеленый','зеленый'],'DARK GREEN':['темно-зеленый','зеленый'],
'MEDIUM BROW':['коричневый'],'DARK BROWN':['темно-коричневый','коричневый'],'BROWN PRINT':['коричневый'],'MEDIUM BLUE':['синий'],'LIGHT BLUE':['светло-голубой','голубой'],'DARK BLUE':['темно-синий','синий'],'NAVY':['темно-синий','синий'],'BLUE PRINT':['синий'],
'MEDIUM GREY':['серый'],'DARK GREY':['темно-серый','серый'],'LIGHT GREY':['светло-серый','серый'],'GREY PRINT':['серый'],'PURPLE/LILA':['сиреневый','лиловый'],'PURPLE/LILAC':['сиреневый','лиловый'],'ORANGE':['оранжевый'],'RED':['красный'],'RED PRINT':['красный'],'YELLOW':['желтый'],
'WINE':['винный','бордовый'],'MAROON':['бордовый'],'MULTICOLOUR':['мультиколор'],'MULTICOLOURED':['мультиколор'],'FUCHSIA':['фуксия'],'CORAL':['коралловый'],'GREEN PRINT':['зеленый'],'BEIGE/CAMEL':['бежевый','светло-коричневый'],'LIGHT KHAKI':['хаки'],'KHAKI':['хаки'],'DARK KHAKI':['хаки'],'MEDIUM KHAK':['хаки'],'BURGUNDY':['бордовый'],'MAROON PRIN':['бордовый'],'ORANGE PRIN':['оранжевый'],'YELLOW PRIN':['желтый'],'LIGHT BROWN':['светло-коричневый','коричневый'],'CAMEL':['бежевый'],'RED/CORAL':['красный','коралловый'],'BEIGE':['бежевый','светло-бежевый'],'NAVY BLUE':['темно-синий','синий'],'CHARCOAL GR':['графит','антрацит','темно-серый','серый']}
def color_ru(en,allowed):
    for c in CAND.get(en.upper().strip(),[]):
        if c in allowed: return c
    return None
MAT={'POLYAMIDE':'полиамид','POLIAMIDA':'полиамид','ELASTANE':'эластан','ELASTANO':'эластан','POLYESTER':'полиэстер','POLIESTER':'полиэстер','COTTON':'хлопок','ALGODON':'хлопок','VISCOSE':'вискоза','MODAL':'модал','NYLON':'нейлон','LYCRA':'лайкра','SILK':'шелк','ACRYLIC':'акрил','WOOL':'шерсть','SILICON':'силикон','POLYURETHANE':'полиуретан','LINEN':'лен','VELVET':'бархат','LYOCELL':'лиоцелл'}
TYPE={'TOP REMOVABLE PAD':'бралетт','TOP HALTER REMOVABLE':'бралетт','TOP':'бралетт','TRIANGULAR':'бралетт','TRIANGULAR PADDED':'бралетт','PADDED HALTER':'мягкая чашка','PADDED':'дублированная чашка','PUSH UP':'пуш-ап','UNDERWIRED BUSTIER':'мягкая чашка'}
BY_STYLE={'4024527':'бралетт','5691558':'мягкая чашка','5691560':'мягкая чашка','5691562':'мягкая чашка'}   # по фото
MODEL={'HIPSTER BRIEF':('хипстеры','средняя'),'PACK HIPSTER BRIEF':('хипстеры','средняя'),'SIDE STRING HIPSTER':('хипстеры','средняя'),'WIDE BRIEF':('брифы','средняя'),'PACK WIDE BRIEF':('брифы','средняя'),
 'BRASILIEN BRIEF':('бразильяна','средняя'),'BRASILIEN WIDE BRIEF':('бразильяна','средняя'),'PACK BRASILIEN BRIEF':('бразильяна','средняя'),'THONG':('тонг','низкая'),'PACK THONG BRIEF':('тонг','низкая'),'SIDE STRING THONG':('стринги','низкая'),'':('брифы','средняя')}
SZ={'XS':'42','S':'44','M':'46','L':'48','XL':'50','XXL':'52'}
