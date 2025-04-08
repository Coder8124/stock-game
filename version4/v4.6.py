# copy of backup incase anything happened between transporting the code
import pygame
import random

import matplotlib.pyplot as plt
from io import BytesIO
# Initialize Pygame
pygame.init()
plt.style.use("fast")
# Screen setup
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stock Market Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GRAY = (200, 200, 200)

textScroll = WIDTH

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Input box for typing in stock numbers
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('lightskyblue3')
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.unicode.isdigit():  # Only allow digits
                    self.text += event.unicode
                self.txt_surface = font.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

# Button class for interaction
class Button:
    def __init__(self, x, y, w, h, text, color=GRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = font.render(self.text, True, BLACK)
        screen.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
                                   self.rect.y + (self.rect.height - text_surface.get_height()) // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
class Stock:
    def __init__(self,name):
        self.name = name
        self.price = random.randint(20,300)
        self.low = -2
        self.high = 3
        self.economy = "Standard" # or upturn, or downturn

    def updateLowHigh(self):
        settings = {
            "Bad Standard" : (-0.45, 0.375),
            "Good Standard": (-0.025, 0.65),
            "Standard" : (-0.05, 0.35),
            "Great Upturn": (-0.015,1.657285),
            "Ok Upturn": (-0.025,1.285),
            "Upturn": (-0.05,0.785),
            "Downturn" : (-0.005,-1.25),
            "Good Downturn" : (-0.005,-0.7225),
            "Bank Account == Cooked" : (-0.35,-2.25),
            "TO THE SKY" : (0.5,4.25),
            "Geopolitical Tensions" : (-0.5,-0.55),
            "Medium" : (-0.005,0.005)
        }
        current_setting = settings[self.economy]
        self.low = current_setting[0]
        self.high = current_setting[1]


# StockMarketGame class with graph integration
class StockMarketGame:
    def __init__(self):
        self.cash = 10000
        self.portfolio = {}
        self.stocks = [Stock("Steel"), Stock("Tech"), Stock("Food"), Stock("Gold"), Stock("Aviation"), Stock("Cars")]
        # self.stock_prices = {"Steel": random.randint(20, 300), "Tech": random.randint(20, 500),
        #                      "Food": random.randint(20, 300), "Gold": random.randint(20, 300),
        #                      "Aviation": random.randint(30,200),"Cars": random.randint(20,300)}
        self.historical_prices = {stock.name: [stock.price] for stock in self.stocks}
        self.turn = 1
        self.selected_stock = None
        self.message = ""  # Add a message attribute
        self.message_surface = font.render(self.message, True, BLACK)
        self.recession_timer = random.randint(360, 480)  # Initialize the recession timer
        self.economy_status_timer = random.randint(30,40)

    def display_market(self):
        y_offset = 50
        for s in self.stocks:
            stock = s.name
            price = s.price
            stock_text = f"{stock}: ${price:.2f}"
            stock_surface = font.render(stock_text, True, BLACK)
            screen.blit(stock_surface, (50, y_offset))
            y_offset += 40

    def display_portfolio(self):
        y_offset = 300
        portfolio_text = "Your Portfolio:"
        portfolio_surface = font.render(portfolio_text, True, BLACK)
        screen.blit(portfolio_surface, (50, y_offset))
        y_offset += 40

        balance_text = f"You have ${self.cash:.2f} in your bank account."
        balance_surface = small_font.render(balance_text, True, BLACK)
        screen.blit(balance_surface, (50, y_offset))
        y_offset += 30

        for stock, shares in self.portfolio.items():
            value = shares * self.findStockPrice(stock)
            portfolio_item_text = f"{stock}: {shares} shares @ ${self.findStockPrice(stock):.2f} (${value:.2f})"
            portfolio_item_surface = small_font.render(portfolio_item_text, True, BLACK)
            screen.blit(portfolio_item_surface, (50, y_offset))
            y_offset += 30
    def display_message(self):
        global textScroll 
        textScroll -= 1
        if textScroll + (len(self.message) * 14) < 0:
            textScroll = WIDTH
        self.message_surface = font.render(self.message, True, BLACK)
        screen.blit(self.message_surface, (textScroll, HEIGHT - 50))
        
    def buy_stock(self, shares_to_buy):
        if not self.selected_stock:
            self.message = "No stock selected!"
            return

        try:
            shares_to_buy = int(shares_to_buy)
            if shares_to_buy <= 0:
                self.message = "Invalid number of shares!"
                return
        except ValueError:
            self.message = "Invalid number of shares!"
            return

        stock_price = self.findStockPrice(self.selected_stock)
        cost = shares_to_buy * stock_price

        if cost > self.cash:
            self.message = "Not enough cash!"
            return

        self.cash -= cost
        self.portfolio[self.selected_stock] = self.portfolio.get(self.selected_stock, 0) + shares_to_buy
        self.message = f"Bought {shares_to_buy} shares of {self.selected_stock} for ${cost:.2f}"
    
    def findStockPrice(self, selected_stock):
        for stock in self.stocks:
            if stock.name == selected_stock:
                return stock.price

    def sell_stock(self, shares_to_sell):
        if not self.selected_stock or self.selected_stock not in self.portfolio:
            self.message = "No stock selected or no shares owned!"
            return
        try:
            shares_to_sell = int(shares_to_sell)
            if shares_to_sell <= 0:
                self.message = "Invalid number of shares!"
                return
        except ValueError:
            self.message = "Invalid number of shares!"
            return

        if shares_to_sell > self.portfolio[self.selected_stock]:
            self.message = "Not enough shares to sell!"
            return

        selected_stock_price = self.findStockPrice(self.selected_stock)
        revenue = shares_to_sell * selected_stock_price

        self.cash += revenue
        self.portfolio[self.selected_stock] -= shares_to_sell

        if self.portfolio[self.selected_stock] == 0:
            del self.portfolio[self.selected_stock]

        self.message = f"Sold {shares_to_sell} shares of {self.selected_stock} for ${revenue:.2f}"

    def hold(self, play):
        if play:
            for s in self.stocks:
                stock = s.name
                s.updateLowHigh()
                change_percentage = random.uniform(s.low, s.high)
                s.price *= (1 + change_percentage / 100)
                s.price = max(1.0, round(s.price, 2))
                self.historical_prices[stock].append(s.price)
            

            self.turn += 1
            self.check_recession()
            self.check_eco_status()

    def check_eco_status(self):
        self.economy_status_timer -= 1
        if self.economy_status_timer <= 0:
            for s in self.stocks:
                self.ecoodds = random.randint(1,100)
                if self.ecoodds >= 1 and self.ecoodds <= 35:
                    s.economy = "Standard"
                if self.ecoodds >= 35 and self.ecoodds <= 45:
                    s.economy = "Good Standard"
                elif self.ecoodds > 45 and self.ecoodds <= 55:
                    s.economy = "Bad Standard"
                if self.ecoodds >= 55 and self.ecoodds <= 65:
                    s.economy = "Great Upturn"
                if self.ecoodds >= 55 and self.ecoodds <= 65:
                    s.economy = "Ok Upturn"
                elif self.ecoodds > 75 and self.ecoodds <= 82:
                    s.economy = "Good Downturn"
                if self.ecoodds >= 83 and self.ecoodds <= 86:
                    s.economy = "Bank Account == Cooked"
                if self.ecoodds >= 87 and self.ecoodds <= 89:
                    s.economy = "TO THE SKY"
                if self.ecoodds >= 90 and self.ecoodds <= 92:
                    s.economy = "Geopolitical Tensions"
                if self.ecoodds >= 93 and self.ecoodds <= 100:
                    s.economy = "Medium"
                print(f"{s.name}: {s.economy}")
                
            self.economy_status_timer = random.randint(30,40)

    def draw_graph(self):
        if not self.selected_stock:
            return None

        plt.figure(figsize=(5.5, 3))
        plt.plot(self.historical_prices[self.selected_stock], marker='o', linestyle='-', color='blue')
        plt.title(f"{self.selected_stock} Stock Prices")
        plt.xlabel("Weeks")
        plt.ylabel("Price ($)")

        buf = BytesIO()
        plt.savefig(buf, format="webp")
        buf.seek(0)

        graph_surface = pygame.image.load(buf)

        buf.close()
        plt.close()

        return graph_surface

    def check_recession(self):
        self.recession_timer -= 1
        if self.recession_timer <= 0:
            recession_type = "Fake"
            odds = random.randint(1,100)
            if odds >= 1 and odds <= 5:
                recession_type = "Fake"
            elif odds > 5 and odds <= 80:
                recession_type = "Stock Market Dip"
            elif odds > 80 and odds <= 95:
                recession_type = "Recession"
            elif odds > 95 and odds <= 100:
                recession_type = "Depression"


            self.trigger_recession(recession_type)
            self.recession_timer = random.randint(200, 300)  # Reset the timer
# 3 levels of recessions, 1 is a common recession & stock prices drop by 10-30%. 2 is a medium recession & prices drop by 40-60%. 3 is depression & prices drop the current 80-95%
    def trigger_recession(self, recession_type):

        types = {
            "Fake" : (-1,1),
            "Stock Market Dip" : (-3, -25),
            "Recession" : (-30, -40),
            "Depression": (-50, -60)
        }

        settings = types[recession_type]
        if recession_type == "Standard":
            self.message = f"{recession_type} Occurs! Stock Prices Drop!"
        elif recession_type == "Recession":
            self.message = f"{recession_type} Hits! Stock Prices Drop!"
        elif recession_type == "Depression":
            self.message = f"{recession_type} Hits! Stock Prices Drop! (Emotional Damage... your bank account is worth as much as a cabbage)"
        elif recession_type == "Fake":
            self.message = f"Get trolled"

        for stock in self.stocks:
            # Apply a significant negative change to stock prices
            change_percentage = random.uniform(settings[0], settings[1])  
            stock.price *= (1 + change_percentage / 100)
            stock.price = max(1.0, round(stock.price, 2))
            # self.historical_prices[stock].append(stock.price)


# Game loop setup
game_running = True
game_instance = StockMarketGame()

# Buttons for interaction
buy_button = Button(800, 100, 150, 50, "Buy")
sell_button = Button(800, 200, 150, 50, "Sell")
hold_button = Button(800, 300, 150, 50, "Play/Pause")
quit_button = Button(800, 400, 150, 50, "Quit")
close_graph_button = Button(400, 350, 150, 50, "Close Graph")

# Input box
input_box = InputBox(800, 50, 140, 32)
play = False
start = True

drawGraph = True
drawGraphTimer = 0
drawGraphTimerDEF = 5

timer = 0
timer_speed = 0.5
# timer_start = 60 * timer_speed
timer_start = 1
clock = pygame.time.Clock()
while game_running:
    screen.fill(WHITE)
    if timer == 0:
        game_instance.hold(play)
        timer = timer_start
    else:
        timer -= 1

    # Display market and portfolio information
    game_instance.display_market()
    game_instance.display_portfolio()
    game_instance.display_message()  # Display the message

    # Draw buttons
    buy_button.draw()
    sell_button.draw()
    hold_button.draw()
    quit_button.draw()
    input_box.draw(screen)

    # Display graph if a stock is selected
    if game_instance.selected_stock:
        if play or start:
            if drawGraphTimer > 0:
                drawGraphTimer -= 1
            else:
                graph_surface = game_instance.draw_graph()
                drawGraphTimer = drawGraphTimerDEF
            start = False
        screen.blit(graph_surface, (200, 25))
        close_graph_button.draw()  # Draw the close graph button

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False

        input_box.handle_event(event)  # Handle the input box events

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if buy_button.is_clicked(mouse_pos):
                game_instance.buy_stock(input_box.text)
                input_box.text = ''  # Clear the input box after buying
            elif sell_button.is_clicked(mouse_pos):
                game_instance.sell_stock(input_box.text)
                input_box.text = ''  # Clear the input box after selling
            elif hold_button.is_clicked(mouse_pos):
                play = not play
            elif quit_button.is_clicked(mouse_pos):
                game_running = False
            elif game_instance.selected_stock and close_graph_button.is_clicked(mouse_pos):
                game_instance.selected_stock = None
            else:
                # Check if a stock is clicked
                y_offset = 50
                stock_clicked = False
                for s in game_instance.stocks:
                    stock_rect = pygame.Rect(50, y_offset, 200, 40)
                    if stock_rect.collidepoint(mouse_pos):
                        game_instance.selected_stock = s.name
                        stock_clicked = True
                        break
                    y_offset += 40

                # If clicked outside stock list and graph area, close the graph
                if not stock_clicked and not (400 <= mouse_pos[0] <= 900 and 50 <= mouse_pos[1] <= 400):
                    game_instance.selected_stock = None
    pygame.display.update()
    clock.tick(60)

pygame.quit()
