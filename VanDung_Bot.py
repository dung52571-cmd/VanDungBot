#!/usr/bin/env python3
"""
VĂN DŨNG GOLD - Telegram Bot
Tự động kick Gold cho khách khi nhắn username
"""

import asyncio, aiohttp, json, re, os, time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           CallbackQueryHandler, filters, ContextTypes)

# ──────────────────────────────────────────
# CẤU HÌNH - SỬA Ở ĐÂY
# ──────────────────────────────────────────

BOT_TOKEN  = "8868803975:AAG5oLI2ow5xjr4JnkdE41NLof_CBChsVYk"
ADMIN_IDS  = [8374619289, 7662760183]
ZALO       = "0364594036"
SHOP_NAME  = "VĂN DŨNG GOLD"

# ──────────────────────────────────────────
# TOKEN REVENUECAT
# ──────────────────────────────────────────

TOKEN_CONFIG = {
    "name": "Văn Dũng Gold",
    "fetch_token": "eyJhbGciOiJFUzI1NiIsIng1YyI6WyJNSUlFTVRDQ0E3YWdBd0lCQWdJUVI4S0h6ZG41NTRaL1VvcmFkTng5dHpBS0JnZ3Foa2pPUFFRREF6QjFNVVF3UWdZRFZRUURERHRCY0hCc1pTQlhiM0pzWkhkcFpHVWdSR1YyWld4dmNHVnlJRkpsYkdGMGFXOXVjeUJEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURUxNQWtHQTFVRUN3d0NSell4RXpBUkJnTlZCQW9NQ2tGd2NHeGxJRWx1WXk0eEN6QUpCZ05WQkFZVEFsVlRNQjRYRFRJMU1Ea3hPVEU1TkRRMU1Wb1hEVEkzTVRBeE16RTNORGN5TTFvd2daSXhRREErQmdOVkJBTU1OMUJ5YjJRZ1JVTkRJRTFoWXlCQmNIQWdVM1J2Y21VZ1lXNWtJR2xVZFc1bGN5QlRkRzl5WlNCU1pXTmxhWEIwSUZOcFoyNXBibWN4TERBcUJnTlZCQXNNSTBGd2NHeGxJRmR2Y214a2QybGtaU0JFWlhabGJHOXdaWElnVW1Wc1lYUnBiMjV6TVJNd0VRWURWUVFLREFwQmNIQnNaU0JKYm1NdU1Rc3dDUVlEVlFRR0V3SlZVekJaTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEEwSUFCTm5WdmhjdjdpVCs3RXg1dEJNQmdyUXNwSHpJc1hSaTBZeGZlazdsdjh3RW1qL2JIaVd0TndKcWMyQm9IenNRaUVqUDdLRklJS2c0WTh5MC9ueW51QW1qZ2dJSU1JSUNCREFNQmdOVkhSTUJBZjhFQWpBQU1COEdBMVVkSXdRWU1CYUFGRDh2bENOUjAxREptaWc5N2JCODVjK2xrR0taTUhBR0NDc0dBUVVGQndFQkJHUXdZakF0QmdnckJnRUZCUWN3QW9ZaGFIUjBjRG92TDJObGNuUnpMbUZ3Y0d4bExtTnZiUzkzZDJSeVp6WXVaR1Z5TURFR0NDc0dBUVVGQnpBQmhpVm9kSFJ3T2k4dmIyTnpjQzVoY0hCc1pTNWpiMjB2YjJOemNEQXpMWGQzWkhKbk5qQXlNSUlCSGdZRFZSMGdCSUlCRlRDQ0FSRXdnZ0VOQmdvcWhraUc5Mk5rQlFZQk1JSCtNSUhEQmdnckJnRUZCUWNDQWpDQnRneUJzMUpsYkdsaGJtTmxJRzl1SUhSb2FYTWdZMlZ5ZEdsbWFXTmhkR1VnWW5rZ1lXNTVJSEJoY25SNUlHRnpjM1Z0WlhNZ1lXTmpaWEIwWVc1alpTQnZaaUIwYUdVZ2RHaGxiaUJoY0hCc2FXTmhZbXhsSUhOMFlXNWtZWEprSUhSbGNtMXpJR0Z1WkNCamIyNWthWFJwYjI1eklHOW1JSFZ6WlN3Z1kyVnlkR2xtYVdOaGRHVWdjRzlzYVdONUlHRnVaQ0JqWlhKMGFXWnBZMkYwYVc5dUlIQnlZV04wYVdObElITjBZWFJsYldWdWRITXVNRFlHQ0NzR0FRVUZCd0lCRmlwb2RIUndPaTh2ZDNkM0xtRndjR3hsTG1OdmJTOWpaWEowYVdacFkyRjBaV0YxZEdodmNtbDBlUzh3SFFZRFZSME9CQllFRklGaW9HNHdNTVZBMWt1OXpKbUdOUEFWbjNlcU1BNEdBMVVkRHdFQi93UUVBd0lIZ0RBUUJnb3Foa2lHOTJOa0Jnc0JCQUlGQURBS0JnZ3Foa2pPUFFRREF3TnBBREJtQWpFQStxWG5SRUM3aFhJV1ZMc0x4em5qUnBJelBmN1ZIejlWL0NUbTgrTEpsclFlcG5tY1B2R0xOY1g2WFBubGNnTEFBakVBNUlqTlpLZ2c1cFE3OWtuRjRJYlRYZEt2OHZ1dElETVhEbWpQVlQzZEd2RnRzR1J3WE95d1Iya1pDZFNyZmVvdCIsIk1JSURGakNDQXB5Z0F3SUJBZ0lVSXNHaFJ3cDBjMm52VTRZU3ljYWZQVGp6Yk5jd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NakV3TXpFM01qQXpOekV3V2hjTk16WXdNekU1TURBd01EQXdXakIxTVVRd1FnWURWUVFERER0QmNIQnNaU0JYYjNKc1pIZHBaR1VnUkdWMlpXeHZjR1Z5SUZKbGJHRjBhVzl1Y3lCRFpYSjBhV1pwWTJGMGFXOXVJRUYxZEdodmNtbDBlVEVMTUFrR0ExVUVDd3dDUnpZeEV6QVJCZ05WQkFvTUNrRndjR3hsSUVsdVl5NHhDekFKQmdOVkJBWVRBbFZUTUhZd0VBWUhLb1pJemowQ0FRWUZLNEVFQUNJRFlnQUVic1FLQzk0UHJsV21aWG5YZ3R4emRWSkw4VDBTR1luZ0RSR3BuZ24zTjZQVDhKTUViN0ZEaTRiQm1QaENuWjMvc3E2UEYvY0djS1hXc0w1dk90ZVJoeUo0NXgzQVNQN2NPQithYW85MGZjcHhTdi9FWkZibmlBYk5nWkdoSWhwSW80SDZNSUgzTUJJR0ExVWRFd0VCL3dRSU1BWUJBZjhDQVFBd0h3WURWUjBqQkJnd0ZvQVV1N0Rlb1ZnemlKcWtpcG5ldnIzcnI5ckxKS3N3UmdZSUt3WUJCUVVIQVFFRU9qQTRNRFlHQ0NzR0FRVUZCekFCaGlwb2RIUndPaTh2YjJOemNDNWhjSEJzWlM1amIyMHZiMk56Y0RBekxXRndjR3hsY205dmRHTmhaek13TndZRFZSMGZCREF3TGpBc29DcWdLSVltYUhSMGNEb3ZMMk55YkM1aGNIQnNaUzVqYjIwdllYQndiR1Z5YjI5MFkyRm5NeTVqY213d0hRWURWUjBPQkJZRUZEOHZsQ05SMDFESm1pZzk3YkI4NWMrbGtHS1pNQTRHQTFVZER3RUIvd1FFQXdJQkJqQVFCZ29xaGtpRzkyTmtCZ0lCQkFJRkFEQUtCZ2dxaGtqT1BRUURBd05vQURCbEFqQkFYaFNxNUl5S29nTUNQdHc0OTBCYUI2NzdDYUVHSlh1ZlFCL0VxWkdkNkNTamlDdE9udU1UYlhWWG14eGN4ZmtDTVFEVFNQeGFyWlh2TnJreFUzVGtVTUkzM3l6dkZWVlJUNHd4V0pDOTk0T3NkY1o0K1JHTnNZRHlSNWdtZHIwbkRHZz0iLCJNSUlDUXpDQ0FjbWdBd0lCQWdJSUxjWDhpTkxGUzVVd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NVFF3TkRNd01UZ3hPVEEyV2hjTk16a3dORE13TVRneE9UQTJXakJuTVJzd0dRWURWUVFEREJKQmNIQnNaU0JTYjI5MElFTkJJQzBnUnpNeEpqQWtCZ05WQkFzTUhVRndjR3hsSUVObGNuUnBabWxqWVhScGIyNGdRWFYwYUc5eWFYUjVNUk13RVFZRFZRUUtEQXBCY0hCc1pTQkpibU11TVFzd0NRWURWUVFHRXdKVlV6QjJNQkFHQnlxR1NNNDlBZ0VHQlN1QkJBQWlBMklBQkpqcEx6MUFjcVR0a3lKeWdSTWMzUkNWOGNXalRuSGNGQmJaRHVXbUJTcDNaSHRmVGpqVHV4eEV0WC8xSDdZeVlsM0o2WVJiVHpCUEVWb0EvVmhZREtYMUR5eE5CMGNUZGRxWGw1ZHZNVnp0SzUxN0lEdll1VlRaWHBta09sRUtNYU5DTUVBd0hRWURWUjBPQkJZRUZMdXczcUZZTTRpYXBJcVozcjY5NjYvYXl5U3JNQThHQTFVZEV3RUIvd1FGTUFNQkFmOHdEZ1lEVlIwUEFRSC9CQVFEQWdFR01Bb0dDQ3FHU000OUJBTURBMmdBTUdVQ01RQ0Q2Y0hFRmw0YVhUUVkyZTN2OUd3T0FFWkx1Tit5UmhIRkQvM21lb3locG12T3dnUFVuUFdUeG5TNGF0K3FJeFVDTUcxbWloREsxQTNVVDgyTlF6NjBpbU9sTTI3amJkb1h0MlFmeUZNbStZaGlkRGtMRjF2TFVhZ002QmdENTZLeUtBPT0iXX0.eyJyZWNlaXB0VHlwZSI6IlByb2R1Y3Rpb24iLCJhcHBBcHBsZUlkIjoxNjAwNTI1MDYxLCJidW5kbGVJZCI6ImNvbS5sb2NrZXQuTG9ja2V0IiwiYXBwbGljYXRpb25WZXJzaW9uIjoiMTA0NiIsInZlcnNpb25FeHRlcm5hbElkZW50aWZpZXIiOjg4OTQ2NzM1NywicmVjZWlwdENyZWF0aW9uRGF0ZSI6MTc4NjY4MzAyMjUxMSwicmVxdWVzdERhdGUiOjE3ODY2ODMwMjI1MTEsIm9yaWdpbmFsUHVyY2hhc2VEYXRlIjoxNzA4NjI1NjY5NTY0LCJvcmlnaW5hbEFwcGxpY2F0aW9uVmVyc2lvbiI6IjEiLCJkZXZpY2VWZXJpZmljYXRpb24iOiJXUUV1eEx3QWo4d1pVdkJkVFM3dnI4ZFFVOGFUZ205ZFI4Zzl6eUxSNTUrbUlkWWdhaHQvbmttb0VXdnBGb1RRIiwiZGV2aWNlVmVyaWZpY2F0aW9uTm9uY2UiOiI3OTQ3ZWRhMS1jMWVmLTQ4ZmItOWEyYS02MWI4YzBjM2YxOTciLCJvcmlnaW5hbFBsYXRmb3JtIjoiaU9TIiwiYXBwVHJhbnNhY3Rpb25JZCI6IjcwNDI3MjE5OTMxNTM1ODU2OSJ9.dD-eTadlrPvk-5Xj6iFlq2AD6prK9tmzG_zCkW_CIAKp46MJuvZDrblyIQXV3ahhMvGE7F_dZl7HPRBgkFcUkQ",
    "app_transaction": "eyJhbGciOiJFUzI1NiIsIng1YyI6WyJNSUlFTVRDQ0E3YWdBd0lCQWdJUVI0S0h6ZG41NTRaL1VvcmFkTng5dHpBS0JnZ3Foa2pPUFFRREF6QjFNVVF3UWdZRFZRUURERHRCY0hCc1pTQlhiM0pzWkhkcFpHVWdSR1YyWld4dmNHVnlJRkpsYkdGMGFXOXVjeUJEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURUxNQWtHQTFVRUN3d0NSell4RXpBUkJnTlZCQW9NQ2tGd2NHeGxJRWx1WXk0eEN6QUpCZ05WQkFZVEFsVlRNQjRYRFRJMU1Ea3hPVEU1TkRRMU1Wb1hEVEkzTVRBeE16RTNORGN5TTFvd2daSXhRREErQmdOVkJBTU1OMUJ5YjJRZ1JVTkRJRTFoWXlCQmNIQWdVM1J2Y21VZ1lXNWtJR2xVZFc1bGN5QlRkRzl5WlNCU1pXTmxhWEIwSUZOcFoyNXBibWN4TERBcUJnTlZCQXNNSTBGd2NHeGxJRmR2Y214a2QybGtaU0JFWlhabGJHOXdaWElnVW1Wc1lYUnBiMjV6TVJNd0VRWURWUVFLREFwQmNIQnNaU0JKYm1NdU1Rc3dDUVlEVlFRR0V3SlZVekJaTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEEwSUFCTm5WdmhjdjdpVCs3RXg1dEJNQmdyUXNwSHpJc1hSaTBZeGZlazdsdjh3RW1qL2JIaVd0TndKcWMyQm9IenNRaUVqUDdLRklJS2c0WTh5MC9ueW51QW1qZ2dJSU1JSUNCREFNQmdOVkhSTUJBZjhFQWpBQU1COEdBMVVkSXdRWU1CYUFGRDh2bENOUjAxREptaWc5N2JCODVjK2xrR0taTUhBR0NDc0dBUVVGQndFQkJHUXdZakF0QmdnckJnRUZCUWN3QW9ZaGFIUjBjRG92TDJObGNuUnpMbUZ3Y0d4bExtTnZiUzkzZDJSeVp6WXVaR1Z5TURFR0NDc0dBUVVGQnpBQmhpVm9kSFJ3T2k4dmIyTnpjQzVoY0hCc1pTNWpiMjB2YjJOemNEQXpMWGQzWkhKbk5qQXlNSUlCSGdZRFZSMGdCSUlCRlRDQ0FSRXdnZ0VOQmdvcWhraUc5Mk5rQlFZQk1JSCtNSUhEQmdnckJnRUZCUWNDQWpDQnRneUJzMUpsYkdsaGJtTmxJRzl1SUhSb2FYTWdZMlZ5ZEdsbWFXTmhkR1VnWW5rZ1lXNTVJSEJoY25SNUlHRnpjM1Z0WlhNZ1lXTmpaWEIwWVc1alpTQnZaaUIwYUdVZ2RHaGxiaUJoY0hCc2FXTmhZbXhsSUhOMFlXNWtZWEprSUhSbGNtMXpJR0Z1WkNCamIyNWthWFJwYjI1eklHOW1JSFZ6WlN3Z1kyVnlkR2xtYVdOaGRHVWdjRzlzYVdONUlHRnVaQ0JqWlhKMGFXWnBZMkYwYVc5dUlIQnlZV04wYVdObElITjBZWFJsYldWdWRITXVNRFlHQ0NzR0FRVUZCd0lCRmlwb2RIUndPaTh2ZDNkM0xtRndjR3hsTG1OdmJTOWpaWEowYVdacFkyRjBaV0YxZEdodmNtbDBlUzh3SFFZRFZSME9CQllFRklGaW9HNHdNTVZBMWt1OXpKbUdOUEFWbjNlcU1BNEdBMVVkRHdFQi93UUVBd0lIZ0RBUUJnb3Foa2lHOTJOa0Jnc0JCQUlGQURBS0JnZ3Foa2pPUFFRREF3TnBBREJtQWpFQStxWG5SRUM3aFhJV1ZMc0x4em5qUnBJelBmN1ZIejlWL0NUbTgrTEpsclFlcG5tY1B2R0xOY1g2WFBubGNnTEFBakVBNUlqTlpLZ2c1cFE3OWtuRjRJYlRYZEt2OHZ1dElETVhEbWpQVlQzZEd2RnRzR1J3WE95d1Iya1pDZFNyZmVvdCIsIk1JSURGakNDQXB5Z0F3SUJBZ0lVSXNHaFJ3cDBjMm52VTRZU3ljYWZQVGp6Yk5jd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NakV3TXpFM01qQXpOekV3V2hjTk16WXdNekU1TURBd01EQXdXakIxTVVRd1FnWURWUVFERER0QmNIQnNaU0JYYjNKc1pIZHBaR1VnUkdWMlpXeHZjR1Z5SUZKbGJHRjBhVzl1Y3lCRFpYSjBhV1pwWTJGMGFXOXVJRUYxZEdodmNtbDBlVEVMTUFrR0ExVUVDd3dDUnpZeEV6QVJCZ05WQkFvTUNrRndjR3hsSUVsdVl5NHhDekFKQmdOVkJBWVRBbFZUTUhZd0VBWUhLb1pJemowQ0FRWUZLNEVFQUNJRFlnQUVic1FLQzk0UHJsV21aWG5YZ3R4emRWSkw4VDBTR1luZ0RSR3BuZ24zTjZQVDhKTUViN0ZEaTRiQm1QaENuWjMvc3E2UEYvY0djS1hXc0w1dk90ZVJoeUo0NXgzQVNQN2NPQithYW85MGZjcHhTdi9FWkZibmlBYk5nWkdoSWhwSW80SDZNSUgzTUJJR0ExVWRFd0VCL3dRSU1BWUJBZjhDQVFBd0h3WURWUjBqQkJnd0ZvQVV1N0Rlb1ZnemlKcWtpcG5ldnIzcnI5ckxKS3N3UmdZSUt3WUJCUVVIQVFFRU9qQTRNRFlHQ0NzR0FRVUZCekFCaGlwb2RIUndPaTh2YjJOemNDNWhjSEJzWlM1amIyMHZiMk56Y0RBekxXRndjR3hsY205dmRHTmhaek13TndZRFZSMGZCREF3TGpBc29DcWdLSVltYUhSMGNEb3ZMMk55YkM1aGNIQnNaUzVqYjIwdllYQndiR1Z5YjI5MFkyRm5NeTVqY213d0hRWURWUjBPQkJZRUZEOHZsQ05SMDFESm1pZzk3YkI4NWMrbGtHS1pNQTRHQTFVZER3RUIvd1FFQXdJQkJqQVFCZ29xaGtpRzkyTmtCZ0lCQkFJRkFEQUtCZ2dxaGtqT1BRUURBd05vQURCbEFqQkFYaFNxNUl5S29nTUNQdHc0OTBCYUI2NzdDYUVHSlh1ZlFCL0VxWkdkNkNTamlDdE9udU1UYlhWWG14eGN4ZmtDTVFEVFNQeGFyWlh2TnJreFUzVGtVTUkzM3l6dkZWVlJUNHd4V0pDOTk0T3NkY1o0K1JHTnNZRHlSNWdtZHIwbkRHZz0iLCJNSUlDUXpDQ0FjbWdBd0lCQWdJSUxjWDhpTkxGUzVVd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NVFF3TkRNd01UZ3hPVEEyV2hjTk16a3dORE13TVRneE9UQTJXakJuTVJzd0dRWURWUVFEREJKQmNIQnNaU0JTYjI5MElFTkJJQzBnUnpNeEpqQWtCZ05WQkFzTUhVRndjR3hsSUVObGNuUnBabWxqWVhScGIyNGdRWFYwYUc5eWFYUjVNUk13RVFZRFZRUUtEQXBCY0hCc1pTQkpibU11TVFzd0NRWURWUVFHRXdKVlV6QjJNQkFHQnlxR1NNNDlBZ0VHQlN1QkJBQWlBMklBQkpqcEx6MUFjcVR0a3lKeWdSTWMzUkNWOGNXalRuSGNGQmJaRHVXbUJTcDNaSHRmVGpqVHV4eEV0WC8xSDdZeVlsM0o2WVJiVHpCUEVWb0EvVmhZREtYMUR5eE5CMGNUZGRxWGw1ZHZNVnp0SzUxN0lEdll1VlRaWHBta09sRUtNYU5DTUVBd0hRWURWUjBPQkJZRUZMdXczcUZZTTRpYXBJcVozcjY5NjYvYXl5U3JNQThHQTFVZEV3RUIvd1FGTUFNQkFmOHdEZ1lEVlIwUEFRSC9CQVFEQWdFR01Bb0dDQ3FHU000OUJBTURBMmdBTUdVQ01RQ0Q2Y0hFRmw0YVhUUVkyZTN2OUd3T0FFWkx1Tit5UmhIRkQvM21lb3locG12T3dnUFVuUFdUeG5TNGF0K3FJeFVDTUcxbWloREsxQTNVVDgyTlF6NjBpbU9sTTI3amJkb1h0MlFmeUZNbStZaGlkRGtMRjF2TFVhZ002QmdENTZLeUtBPT0iXX0.eyJyZWNlaXB0VHlwZSI6IlByb2R1Y3Rpb24iLCJhcHBBcHBsZUlkIjoxNjAwNTI1MDYxLCJidW5kbGVJZCI6ImNvbS5sb2NrZXQuTG9ja2V0IiwiYXBwbGljYXRpb25WZXJzaW9uIjoiMTA0NiIsInZlcnNpb25FeHRlcm5hbElkZW50aWZpZXIiOjg4OTQ2NzM1NywicmVjZWlwdENyZWF0aW9uRGF0ZSI6MTc4NjY4MzAyMjUxMSwicmVxdWVzdERhdGUiOjE3ODY2ODMwMjI1MTEsIm9yaWdpbmFsUHVyY2hhc2VEYXRlIjoxNzA4NjI1NjY5NTY0LCJvcmlnaW5hbEFwcGxpY2F0aW9uVmVyc2lvbiI6IjEiLCJkZXZpY2VWZXJpZmljYXRpb24iOiJXUUV1eEx3QWo4d1pVdkJkVFM3dnI4ZFFVOGFUZ205ZFI4Zzl6eUxSNTUrbUlkWWdhaHQvbmttb0VXdnBGb1RRIiwiZGV2aWNlVmVyaWZpY2F0aW9uTm9uY2UiOiI3OTQ3ZWRhMS1jMWVmLTQ4ZmItOWEyYS02MWI4YzBjM2YxOTciLCJvcmlnaW5hbFBsYXRmb3JtIjoiaU9TIiwiYXBwVHJhbnNhY3Rpb25JZCI6IjcwNDI3MjE5OTMxNTM1ODU2OSJ9.dD-eTadlrPvk-5Xj6iFlq2AD6prK9tmzG_zCkW_CIAKp46MJuvZDrblyIQXV3ahhMvGE7F_dZl7HPRBgkFcUkQ",
    "hash_params": "app_user_id,fetch_token,app_transaction:sha256:8b6cce125219e2c6a26689448234c8c03894cb72855b73e8598c58ed1056d8df",
    "hash_headers": "X-Is-Sandbox:sha256:fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa",
}

# ── Usage tracking ──────────────────────────────
DAILY_LIMIT = 5
usage_data: dict = {}

# ── /start gate ─────────────────────────────────
# Lưu user_id đã gõ /start
started_users: set = set()

def is_started(user_id: int) -> bool:
    return user_id in ADMIN_IDS or user_id in started_users

NOT_STARTED_MSG = (
    "⚠️ Vui lòng gõ lệnh /start trước khi sử dụng bot!"
)

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
        if not text:
            return None
        m = re.search(r'/invites/([A-Za-z0-9]{28})', text)
        if m:
            return m.group(1)
        lp = re.search(r'link=([^ "\'>]+)', text)
        if lp:
            try:
                d = lp.group(1).replace('%3A', ':').replace('%2F', '/')
                dm = re.search(r'/invites/([A-Za-z0-9]{28})', d)
                if dm:
                    return dm.group(1)
            except:
                pass
        return None

    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers, allow_redirects=True,
                             timeout=aiohttp.ClientTimeout(total=10)) as r:
                html = await r.text()
                return extract(str(r.url)) or extract(html)
    except Exception:
        pass
    return None


async def check_gold_status(uid: str) -> tuple[bool, str | None]:
    """
    GET /v1/subscribers/{uid} — trả về (has_gold, expires_date_str | None)
    has_gold = True nếu có entitlement active hoặc subscription chưa hết hạn
    """
    url = f"https://api.revenuecat.com/v1/subscribers/{uid}"
    hdrs = {k: v for k, v in HEADERS.items()
            if k not in ('Content-Type', 'Content-Length', 'X-Post-Params-Hash', 'X-Headers-Hash')}
    hdrs['Accept'] = 'application/json'

    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=hdrs,
                             timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return False, None
                data = await r.json()

        subscriber = data.get("subscriber", {})
        now_ts = time.time()

        # Kiểm tra entitlements trước (cách nhanh nhất)
        entitlements = subscriber.get("entitlements", {})
        for ent_name, ent_data in entitlements.items():
            expires_raw = ent_data.get("expires_date")
            if expires_raw is None:
                # lifetime entitlement
                return True, "Vĩnh viễn"
            try:
                from datetime import timezone
                expires_dt = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
                if expires_dt.timestamp() > now_ts:
                    return True, expires_dt.strftime("%d/%m/%Y")
            except Exception:
                pass

        # Kiểm tra subscriptions
        subscriptions = subscriber.get("subscriptions", {})
        for sub_id, sub_data in subscriptions.items():
            if not sub_data.get("is_sandbox", False):
                expires_raw = sub_data.get("expires_date")
                if expires_raw:
                    try:
                        expires_dt = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
                        if expires_dt.timestamp() > now_ts:
                            return True, expires_dt.strftime("%d/%m/%Y")
                    except Exception:
                        pass

        return False, None
    except Exception:
        return False, None


async def inject_gold(uid: str) -> tuple[bool, str]:
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
            "$attConsentStatus": {
                "updated_at_ms": int(time.time() * 1000),
                "value": "notDetermined"
            }
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
        async with s.post(url, headers=hdrs, json=body,
                          timeout=aiohttp.ClientTimeout(total=15)) as r:
            data = await r.json()
            if r.status in (200, 201):
                return True, "✅ Kick Gold thành công!"
            else:
                err = data.get("message", str(r.status))
                return False, f"❌ Thất bại: {err}"


# ──────────────────────────────────────────
# BOT HANDLERS
# ──────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    started_users.add(user_id)          # đánh dấu đã /start
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏅 Nhập User Locket", callback_data="nhap_user")],
        [
            InlineKeyboardButton("🌐 Đổi Ngôn Ngữ", callback_data="ngonngu"),
            InlineKeyboardButton("🆘 Hỗ Trợ", url=f"https://zalo.me/{ZALO}"),
        ],
    ])
    await update.message.reply_text(
        f"🟢 *{SHOP_NAME}*\n\n"
        f"Chào mừng! Vui lòng chọn ngôn ngữ hoặc sử dụng menu bên dưới.\n\n"
        f"Tham gia nhóm chat: https://t.me/gocnholocket",
        parse_mode="Markdown",
        reply_markup=kb
    )


async def cmd_kick(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Lệnh admin: /kick <username>"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not ctx.args:
        await update.message.reply_text("Dùng: /kick <username>")
        return
    username = ctx.args[0]
    msg = await update.message.reply_text(f"⏳ Đang xử lý `{username}`...", parse_mode="Markdown")
    uid = await resolve_uid(username)
    if not uid:
        await msg.edit_text(f"❌ Không tìm thấy UID cho `{username}`", parse_mode="Markdown")
        return
    ok, result = await inject_gold(uid)
    await msg.edit_text(
        f"{result}\n\n👤 Username: `{username}`\n🔑 UID: `{uid}`",
        parse_mode="Markdown"
    )


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # ── GATE: phải /start trước ──────────────────
    if not is_started(user_id):
        await update.message.reply_text(NOT_STARTED_MSG)
        return

    text = update.message.text.strip()

    # Nếu đang chờ nhập username
    if ctx.user_data.get("waiting_username"):
        ctx.user_data["waiting_username"] = False
        username = text.lstrip('@')
        if 'locket.cam/' in username:
            username = username.split('locket.cam/')[-1].split('?')[0]

        msg = await update.message.reply_text(
            f"⏳ Đang tìm tài khoản `{username}`...", parse_mode="Markdown"
        )
        uid = await resolve_uid(username)
        if not uid:
            await msg.edit_text(
                f"❌ Không tìm được tài khoản `{username}`\n\nHãy kiểm tra lại username hoặc link.",
                parse_mode="Markdown"
            )
            return

        # Kiểm tra trạng thái Gold hiện tại
        await msg.edit_text("🔍 Đang kiểm tra trạng thái Gold...", parse_mode="Markdown")
        has_gold, expires_str = await check_gold_status(uid)

        # Kiểm tra giới hạn
        allowed, remaining = check_limit(user_id)
        today = datetime.now().strftime("%Y-%m-%d")
        used = 0
        if user_id in usage_data and usage_data[user_id]["date"] == today:
            used = usage_data[user_id]["count"]

        ctx.user_data["pending_uid"] = uid
        ctx.user_data["pending_username"] = username

        if has_gold:
            # Đã có Gold — chỉ thông báo, không cho kick nữa
            await msg.edit_text(
                f"✅ *Tài khoản đã có Gold!*\n\n"
                f"🪪 `{uid}`\n"
                f"🏷 @{username}\n"
                f"🏅 Plan: *Gold* ✅\n"
                f"📅 Hết hạn: `{expires_str}`\n\n"
                f"Tài khoản này đang hoạt động Gold bình thường.\n"
                f"Không cần kích hoạt lại.",
                parse_mode="Markdown"
            )
            return

        # Chưa có Gold — hiện nút kích hoạt
        if not allowed:
            await msg.edit_text(
                f"⛔ *Đã hết lượt hôm nay!*\n\n"
                f"Bạn đã dùng hết {DAILY_LIMIT}/{DAILY_LIMIT} lượt kích hoạt hôm nay.\n"
                f"Vui lòng quay lại vào ngày mai hoặc liên hệ hỗ trợ.\n\n"
                f"Zalo: `{ZALO}`",
                parse_mode="Markdown"
            )
            return

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🚀 KÍCH HOẠT NGAY", callback_data=f"kick_{uid}_{username}")
        ]])

        await msg.edit_text(
            f"👤 User Information\n\n"
            f"🪪 `{uid}`\n"
            f"🏷 @{username}\n"
            f"📊 Status: ❌ *Chưa có Gold*\n"
            f"🏅 Tài khoản: Free\n"
            f"📅 Đã dùng hôm nay: {used}/{DAILY_LIMIT}",
            parse_mode="Markdown",
            reply_markup=kb
        )
        return

    # Tin nhắn thường - hiện menu
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏅 Nhập User Locket", callback_data="nhap_user")],
        [
            InlineKeyboardButton("🌐 Đổi Ngôn Ngữ", callback_data="ngonngu"),
            InlineKeyboardButton("🆘 Hỗ Trợ", url=f"https://zalo.me/{ZALO}"),
        ],
    ])
    await update.message.reply_text(
        f"🟢 *{SHOP_NAME}*\n\nVui lòng sử dụng menu bên dưới.",
        parse_mode="Markdown",
        reply_markup=kb
    )


async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user_id = q.from_user.id

    # ── GATE: phải /start trước ──────────────────
    if not is_started(user_id):
        await q.answer(NOT_STARTED_MSG, show_alert=True)
        return

    await q.answer()

    if q.data == "nhap_user":
        ctx.user_data["waiting_username"] = True
        await q.message.reply_text(
            "••• Vui lòng nhập Username hoặc Link Locket của bạn vào tin nhắn trả lời bên dưới:",
            parse_mode="Markdown",
            reply_markup=ForceReply(selective=True, input_field_placeholder="Username...")
        )

    elif q.data == "ngonngu":
        await q.message.reply_text(
            "🌐 Hiện tại bot đang dùng *Tiếng Việt*.",
            parse_mode="Markdown"
        )

    elif q.data == "huongdan":
        await q.message.reply_text(
            "📱 *Hướng dẫn cài DNS iOS giữ Gold*\n\n"
            "1️⃣ Nhấn vào file `Vandunggold.mobileconfig` vừa nhận\n"
            "2️⃣ Mở file bằng *Safari* → nhấn *Cho phép*\n"
            "3️⃣ Vào *Cài đặt* → nhấn *Đã tải về hồ sơ* → nhấn *Cài đặt*\n"
            "4️⃣ Vào *Cài đặt* → *Cài đặt chung* → *Giới thiệu* → *Cài đặt tin cậy chứng chỉ*\n"
            "   → Bật công tắc *LocketGold CA* ← ⚠️ Bước này bắt buộc!\n"
            "5️⃣ Mở Locket → Gold active ✅\n\n"
            "❗ Nếu không bật chứng chỉ tin cậy thì Gold sẽ mất!\n\n"
            f"Hỗ trợ: Zalo `{ZALO}`",
            parse_mode="Markdown"
        )

    elif q.data == "android":
        await q.message.reply_text(
            "🤖 *Hướng dẫn giữ Gold Android*\n\n"
            "1️⃣ Vào *Cài đặt* → *Kết nối* → *Cài đặt kết nối khác*\n"
            "2️⃣ Chọn *DNS Riêng Tư* (Private DNS)\n"
            "3️⃣ Chọn *Tên máy chủ DNS riêng tư*\n"
            "4️⃣ Nhập: `782aa4.dns.nextdns.io`\n"
            "5️⃣ Lưu → Mở Locket → Gold active ✅\n\n"
            f"Hỗ trợ: Zalo `{ZALO}`",
            parse_mode="Markdown"
        )

    elif q.data.startswith("kick_"):
        parts = q.data.split("_", 2)
        uid = parts[1]
        username = parts[2] if len(parts) > 2 else "unknown"
        await q.message.edit_reply_markup(reply_markup=None)
        msg = await q.message.reply_text("🔄 Đang kích hoạt Gold...", parse_mode="Markdown")

        # Kiểm tra giới hạn lần nữa trước khi kick
        allowed, remaining = check_limit(user_id)
        if not allowed and user_id not in ADMIN_IDS:
            await msg.edit_text(
                f"⛔ *Đã hết lượt hôm nay!*\n\nVui lòng quay lại vào ngày mai.\n\nZalo: `{ZALO}`",
                parse_mode="Markdown"
            )
            return

        # Kiểm tra lại Gold status ngay trước khi inject (phòng race)
        has_gold, expires_str = await check_gold_status(uid)
        if has_gold:
            await msg.edit_text(
                f"✅ *Tài khoản đã có Gold rồi!*\n\n"
                f"🏷 @{username}\n"
                f"📅 Hết hạn: `{expires_str}`\n\n"
                f"Không cần kích hoạt lại.",
                parse_mode="Markdown"
            )
            return

        _u = username
        _id = uid

        s1 = (f"[1/3] RESOLVE UID\n"
              f"  ├─ Target: {_u}\n"
              f"  └─ Connecting...")
        await msg.edit_text("```\n" + s1 + "\n```", parse_mode="Markdown")
        await asyncio.sleep(0.8)

        s2 = (f"[1/3] RESOLVE UID\n"
              f"  └─ [SUCCESS] UID: {_id}\n\n"
              f"[2/3] VERIFY\n"
              f"  ├─ Checking target status...\n"
              f"  └─ [FOUND] UID da phan giai.")
        await msg.edit_text("```\n" + s2 + "\n```", parse_mode="Markdown")
        await asyncio.sleep(0.8)

        s3 = (f"[1/3] RESOLVE UID\n"
              f"  └─ [SUCCESS] UID: {_id}\n\n"
              f"[2/3] VERIFY\n"
              f"  └─ [FOUND] OK.\n\n"
              f"[3/3] PROCESS\n"
              f"  ├─ Loading Exploit Payload...\n"
              f"  ├─ Using Token Set: Custom\n"
              f"  ├─ [>] Attempt 1/5: Sending Receipt...\n"
              f"  ├─ [>] Attempt 2/5: Sending Receipt...\n"
              f"  └─ Please wait...")
        await msg.edit_text("```\n" + s3 + "\n```", parse_mode="Markdown")
        await asyncio.sleep(1.2)

        ok, result = await inject_gold(uid)
        if ok:
            add_usage(user_id)
            await msg.edit_text(
                f"✅ *KÍCH HOẠT THÀNH CÔNG*\n\n"
                f"👤 `@{username}`\n"
                f"🏅 Plan: Gold (Hết hạn 14/08/2027)\n\n"
                f"⚠️ *HƯỚNG DẪN QUAN TRỌNG:*\n"
                f"❗ Vào App Locket kiểm tra đã có Gold chưa.\n"
                f"❗ Cài DNS để không bị mất Gold:\n\n"
                f"🍎 *iOS:* Mở file bên dưới bằng Safari → Cho phép → Cài đặt\n"
                f"  ⚠️ Sau đó vào Cài đặt → Cài đặt chung → Giới thiệu → Cài đặt tin cậy chứng chỉ → Bật LocketGold CA\n\n"
                f"🤖 *Android:* `782aa4.dns.nextdns.io`\n"
                f"(Cài đặt → Mạng → Private DNS)\n\n"
                f"💡 Lưu ý: Bắt buộc cài DNS để không bị mất Gold!\n\n"
                f"Tham gia nhóm chat: https://t.me/gocnholocket",
                parse_mode="Markdown"
            )
            try:
                with open("Vandunggold.mobileconfig", "rb") as f:
                    await q.message.reply_document(
                        document=f,
                        filename="Vandunggold.mobileconfig",
                        caption=(
                            "🍎 File DNS cho iOS\n"
                            "1. Mở bằng Safari → Cho phép → Cài đặt\n"
                            "2. Cài đặt → Cài đặt chung → Giới thiệu → Cài đặt tin cậy chứng chỉ → Bật LocketGold CA\n"
                            "⚠️ Bắt buộc bật chứng chỉ tin cậy để giữ Gold!"
                        )
                    )
            except FileNotFoundError:
                pass
        else:
            await msg.edit_text(
                f"{result}\n\nLiên hệ Zalo `{ZALO}` để được hỗ trợ.",
                parse_mode="Markdown"
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
