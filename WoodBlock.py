import hashlib
import datetime
import json

def get_indentation( s ):
    ls = len( s )
    if ls < 14:
        dif = 14 - ls
        return s + ":" + " " * dif
    return s + ":\t"
    
def ammount_valid( self, good, needed ):
    #print( needed )
    #print( getattr( self, good ) )
    if( getattr( self, good ) > needed ):
        return True
    else:
        return False

def calculate_percentage_difference(number1, number2):
    return float((number1 - number2) / number1) * 100

class Block:
    def __init__(self, data, previous_hash):
        self.timestamp = datetime.datetime.utcnow()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calc_hash()
  
    def calc_hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.data).encode('utf-8'))
        return sha.hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.chain.append(self.create_genesis_block())
        
        self.cash = 0               # 1 cash = 1 USD
        
        """
        self.raw_iron = 0           # 1 iron = 100 lb iron
        
        # 1 raw iron = .97 smelted iron, 0.03 slag
        self.smelted_iron = 0       # 1 smelted iron    = 100 lb 
        self.scrap_slag = 0         # 1 slag iron       = 100 lb
        """
    def inventory( self ):
        #print( self.__dict__ )
        res_str = "  _______________________________\n"
        res_str += "/ Inventory: |                   \n"
        res_str += "|____________|\n"
        res_str += "|\n"
        for key, value in self.__dict__.items():
            if( key == "chain" ):
                pass
            else:
                res_str += "|\t" + get_indentation( key) + str( value ) + "\n"
        res_str += "\______________________________"
        return res_str
        
    def buy( self, item_name, amount, PPU ):
        cost = float( amount * PPU )
        if( cost <= self.cash ):
            self.take_cash( cost )
            self.add( item_name, amount )
        else:
           print( "Error: You do not have enough cash to do this transaction!" )
        
    def sell( self, item_name, amount, PPU ):
        cost = float( amount * PPU )
        try:
            self.remove( item_name, amount )
            self.add_cash( cost )
        except:
            try:
                print( "Error: You do not have enough " + str( item_name ) + " to do this transaction! You have: " + str( getattr( self, item_name ) ) )
            except:
                print( "Error: You do not have enough " + str( item_name ) + " to do this transaction! You have: 0" )
            return 
        
    def create_genesis_block(self):
        return Block("Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calc_hash()
        self.chain.append(new_block)
        return new_block.hash

    def add_cash(self, amount):
        self.cash += amount
        data = {
            "type": "add",
            "amount": amount,
            "total_amount": self.cash
        }
        new_block = Block(data, self.get_latest_block().hash)
        self.add_block(new_block)

    def take_cash(self, amount):
        if( amount <= self.cash ):
            self.cash -= amount
            data = {
                "type": "add",
                "amount": amount,
                "total_amount": self.cash
            }
            new_block = Block(data, self.get_latest_block().hash)
            self.add_block(new_block)
        else:
            print( "Error: You do not have enough cash to do this transaction!" )
        
    def add( self, item_name, amount ):
        setattr( self, item_name, amount )
        data = {
            "type": "add",
            "material": item_name,
            "amount": amount,
            "total_amount": getattr( self, item_name )
        }
        new_block = Block( data, self.get_latest_block(  ).hash )
        return self.add_block( new_block )        
        
    def remove( self, item_name, amount ):
        try:
            if( getattr( self, item_name ) >= amount ):
                setattr( self, item_name, getattr( self, item_name ) - amount )
                data = {
                    "type": "remove",
                    "material": item_name,
                    "amount": amount,
                    "total_amount": getattr( self, item_name )
                }
            else:
                print( "Error: You do not have enough of this item in the system!" )
        except:
            print( "Error: This item doesn't exist in the system!" )
            
        data = {
            "type": "add",
            "material": item_name,
            "amount": amount,
            "total_amount": getattr( self, item_name )
        }
        new_block = Block( data, self.get_latest_block(  ).hash )
        return self.add_block( new_block )
        
    
    def add_raw_iron(self, amount):
        self.raw_iron_amount += amount
        data = {
            "type": "add",
            "amount": amount,
            "total_amount": self.raw_iron_amount
        }
        new_block = Block(data, self.get_latest_block().hash)
        self.add_block(new_block)

    def smelt( self, amount, material ): # Transaction( Material, Ammount ) -> Results( depend on mats ). But iron should be: smelted_iron, iron_slag
        # TODO: Add taking away the cost of the smelting
    
        if( material == "raw_iron" ):
            print( "Smelt the raw Iron!!" )
                   
            try:
                if ( self.raw_iron < amount):
                    print("Error: Not enough raw iron available")
                    return
            except:
                print("Error: This item is most likely not in the system")
                return

            # Smelting done here!
            
            # Remove Iron
            self.remove( "raw_iron", amount )
            
            # Add Slag
            self.add( "iron_slag", float( amount * 0.25 ) )
            
            # Add Smelted Iron
            self.add( "smelted_iron", float( amount * 0.75 ) )
             
            #self.take_cash( 10 ) # 10 $ to smelt iron
             
            data = {
                "type": "take",
                "amount": amount,
                "smelted_iron": self.smelted_iron,
                "iron_slag": self.iron_slag,
                "raw_iron": self.raw_iron
            }
        
        new_block = Block(data, self.get_latest_block().hash)
        self.add_block(new_block)
        return amount
        
    def produce( self, amount, product  ): # Transaction( Material, Ammount ) -> Results( depend on mats ). But iron should be: smelted_iron, iron_slag
        # TODO: Add taking away the cost of the smelting
        
        if( product == "iron_nails" ):
            input = "smelted_iron"
            product_yeild = 0.9
            #BPs = [ { "name": "iron_scrap", "yeild": "0.1" } ]
            
            #for number in BPs:
            #    print( getattr( json.loads( number ), "yeild" ) )
            #if( Yeild != 1 ):
            #    pritn( "Error: Byproduct != 1 error" )
            
            
            
            #nails need to have an ammount of smelted iron to create
            #first, we need to see if this is even possible
            # 1 lbs of smelted iron = .9 lbs of nails 
            
            # convert amount to amount_needed
            needed = float( amount / product_yeild )
            #print( "SDFS:\t" + str( needed )            )
            if( not ammount_valid( self, "smelted_iron", needed ) ): 
                print( "Error: You do not have enough smelted_iron to do this!" )
                return
            
            print( "Press the Nails!!" )

            # Smelting done here!
            
            # Remove Iron
            self.remove( "smelted_iron", needed )
            
            # Add Slag
            self.add( "iron_scrap", float( needed * 0.1 ) )
            
            # Add Smelted Iron
            self.add( "iron_nails", amount )
             
            #self.take_cash( 10 ) # 10 $ to smelt iron
             
            data = {
                "type": "produce",
                "amount": amount,
                "smelted_iron": self.smelted_iron,
                "iron_nails": self.iron_nails,
                "iron_scrap": self.iron_scrap
            }
        
        new_block = Block(data, self.get_latest_block().hash)
        self.add_block(new_block)
        return amount


def main():
    # Create a new blockchain
    ironchain = Blockchain()
    print( ironchain.inventory(  ) )

    print( "Add $50,000" )
    
    # Add some cash to the blockchain
    ironchain.add( "cash", 50000 )
    
    #print( blockchain.get_latest_block().hash )
    print( ironchain.inventory(  ) )
    print( "Buy iron @ $0.055 per lb" )
    
    PPU = 0.055 # cost per pound of raw iron
    LBs = 5000
    ironchain.buy( "raw_iron", LBs, PPU )
    
    print( ironchain.inventory(  ) )
    #print( blockchain.get_latest_block().hash )

    # Smelt 5000 some of our raw iron
    CPU = 
    smelted_iron = ironchain.smelt( 5000, "raw_iron", CPU )
    print( ironchain.inventory(  ) )
    
    nails_allowed = smelted_iron * 0.5
    
    # Smelt 5000 some of our raw iron
    nails = ironchain.produce( nails_allowed, "iron_nails" )
    
    print( ironchain.inventory(  ) )
    
    PPU_Nails = 1.28 # cost per pound of raw iron
    ironchain.sell( "iron_nails", nails, PPU_Nails )
    
    PPU_scrap_iron = .04
    ironchain.sell( "iron_nails", nails, PPU_scrap_iron )

    print( ironchain.inventory(  ) )
    
main()