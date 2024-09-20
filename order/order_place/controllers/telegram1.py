from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from asgiref.sync import sync_to_async
from pathlib import Path
app = Path(__file__).resolve().parent.parent.parent
import sys
sys.path.append(str(app))
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order.settings')
django.setup()
import httpx 
from order_place.models import User as u
from django.contrib.auth.models import User

bot = Bot ('Telegram_token')
dp = Dispatcher()


TOKEN                  = "Supplier_token"
VPRN		           = 'VPRN'

main_params  = {
    'vpnr': VPRN,
    'authcode': TOKEN
}

@dp.message(Command(commands = 'orders'))
async def send_help ( message:types.Message):
    try:
        users = await  sync_to_async(list)(User.objects.all())
        total = 0
        site_qty = 0
        for user in users:
            user_name = user.username
            orders = await sync_to_async(list)(u.objects.filter(user_id = user_name, order_status = True))
            if orders:
                await message.answer(f'{user_name} ordered:')
                for order in orders:
                    site_qty += order.item_qty
                    total += order.item_price*order.item_qty
                    await message.answer(f'{order.item_name}\n{order.item_qty} {order.item_price}')
                await message.answer('-                                          -')
            else:
                await message.answer(f'{user_name} no order:')
                await message.answer('-                                          -')
        await message.answer(f'Buy={(total/1.12):.2f} Sell={total:.2f} Profit={(total - total/1.12):.2f}')
        order_nr = await sync_to_async(u.objects.filter(order_status = True).last)()
        if order_nr:
            async with httpx.AsyncClient() as c:
                response = await c.get("Suppliers_url" + str(order_nr.order_id), params = main_params )
                if response.is_success:
                    datas = response.json()
                    await message.answer(f'Order Nr: {order_nr.order_id}, Total Site: {(total/1.12):.2f} Yuk: {datas["totals"]["sub_total"]}, Qty Site: {site_qty} Yuk: {datas["totals"]["total_quantity"]}')
    except Exception as e:
        await message.answer(f"Error: {e}") 
    
                                        
async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
