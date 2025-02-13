#v2 (with graphs) (last decently stable version)
import pygame
import random
import matplotlib.pyplot as plt
from io import BytesIO


# Initialize Pygame
pygame.init()


# Screen setup
WIDTH, HEIGHT = 1000, 700  # Increased size to accommodate graphs
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stock Market Game")


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GRAY = (200, 200, 200)


# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)




# Button class (unchanged)
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




# StockMarketGame class with graph integration
class StockMarketGame:
   def __init__(self):
       self.cash = 10000
       self.portfolio = {}
       self.stock_prices = {"BH": random.randint(20, 900), "CD": random.randint(20, 900),
                            "AG": random.randint(20, 900), "JA": random.randint(20, 900)}
       self.historical_prices = {stock: [price] for stock, price in self.stock_prices.items()}
       self.turn = 1
       self.selected_stock = None


   def display_market(self):
       y_offset = 50
       for stock, price in self.stock_prices.items():
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


       for stock, shares in self.portfolio.items():
           value = shares * self.stock_prices[stock]
           portfolio_item_text = f"{stock}: {shares} shares @ ${self.stock_prices[stock]:.2f} (${value:.2f})"
           portfolio_item_surface = small_font.render(portfolio_item_text, True, BLACK)
           screen.blit(portfolio_item_surface, (50, y_offset))
           y_offset += 30


   def buy_stock(self):
       if not self.selected_stock:
           return
       stock_price = self.stock_prices[self.selected_stock]
       shares_to_buy = int(input(f"How many shares of {self.selected_stock} do you want to buy? "))
       cost = shares_to_buy * stock_price


       if cost > self.cash:
           print("Not enough cash!")
           return


       self.cash -= cost
       self.portfolio[self.selected_stock] = self.portfolio.get(self.selected_stock, 0) + shares_to_buy


   def sell_stock(self):
       if not self.selected_stock or self.selected_stock not in self.portfolio:
           return
       shares_to_sell = int(input(f"How many shares of {self.selected_stock} do you want to sell? "))


       if shares_to_sell > self.portfolio[self.selected_stock]:
           print("You don't own that many shares!")
           return


       revenue = shares_to_sell * self.stock_prices[self.selected_stock]
       self.cash += revenue
       self.portfolio[self.selected_stock] -= shares_to_sell


       if self.portfolio[self.selected_stock] == 0:
           del self.portfolio[self.selected_stock]


   def hold(self):
       for stock in self.stock_prices:
           change_percentage = random.uniform(-10, 10)
           self.stock_prices[stock] *= (1 + change_percentage / 100)
           self.stock_prices[stock] = max(1.0, round(self.stock_prices[stock], 2))
           self.historical_prices[stock].append(self.stock_prices[stock])


       # Earnings report every few turns
       if self.turn % 4 == 0:
           earnings_stock = random.choice(list(self.stock_prices.keys()))
           change_percentage = random.uniform(-50, 50)
           print(f"Earnings report for {earnings_stock}! Price changes by {change_percentage:.2f}%")
           self.stock_prices[earnings_stock] *= (1 + change_percentage / 100)
           self.historical_prices[earnings_stock][-1] = self.stock_prices[earnings_stock]


       self.turn += 1


   def draw_graph(self, stock):
       plt.figure(figsize=(5, 3))
       plt.plot(self.historical_prices[stock], marker='o', linestyle='-', color='blue')
       plt.title(f"{stock} Stock Prices")
       plt.xlabel("Days")
       plt.ylabel("Price ($)")
       plt.grid(True)


       buf = BytesIO()
       plt.savefig(buf, format="PNG")
       buf.seek(0)
       plt.close()


       graph_surface = pygame.image.load(buf, "PNG")
       buf.close()


       return graph_surface




# Game loop setup
game_running = True
game_instance = StockMarketGame()


# Buttons for interaction
buy_button = Button(800, 100, 150, 50, "Buy")
sell_button = Button(800, 200, 150, 50, "Sell")
hold_button = Button(800, 300, 150, 50, "Hold")
quit_button = Button(800, 400, 150, 50, "Quit")


while game_running:
   screen.fill(WHITE)


   # Display market and portfolio information
   game_instance.display_market()
   game_instance.display_portfolio()


   # Draw buttons
   buy_button.draw()
   sell_button.draw()
   hold_button.draw()
   quit_button.draw()


   # Display graph if a stock is selected
   if game_instance.selected_stock:
       graph_surface = game_instance.draw_graph(game_instance.selected_stock)
       screen.blit(graph_surface, (400, 50))


   # Event handling
   for event in pygame.event.get():
       if event.type == pygame.QUIT:
           game_running = False


       if event.type == pygame.MOUSEBUTTONDOWN:
           mouse_pos = event.pos


           if buy_button.is_clicked(mouse_pos):
               game_instance.buy_stock()
           elif sell_button.is_clicked(mouse_pos):
               game_instance.sell_stock()
           elif hold_button.is_clicked(mouse_pos):
               game_instance.hold()
           elif quit_button.is_clicked(mouse_pos):
               game_running = False


           # Check if a stock is clicked
           y_offset = 50
           for stock in game_instance.stock_prices:
               stock_rect = pygame.Rect(50, y_offset, 200, 40)
               if stock_rect.collidepoint(mouse_pos):
                   game_instance.selected_stock = stock
               y_offset += 40


   pygame.display.update()


pygame.quit()
