from flask import Flask, render_template, request,jsonify
import pymongo
import json
import pprint
import pandas as pd
from main import walmartScraper,safewayScraper,krogerScraper
from datetime import date
from bson import ObjectId
from flask_cors import CORS
from bson.json_util import dumps
import  datetime

app = Flask(__name__)
CORS(app,origins=['http://localhost:3000'])
port=8000

client = pymongo.MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
database = client["web-scraper"]  # Replace 'mydatabase' with your database name




# scrape a product data 
def productScrap(product_url):
   
    if(product_url['platform'] == 'WALMART'):
        result1 = walmartScraper(product_url)
        if "url" in result1:
            return  result1
    elif(product_url['platform'] == 'KROGER'): 
        result2 = krogerScraper(product_url) 
        if "url" in result2:
            return  result2
                
    else:
        result3 = safewayScraper(product_url) 
        if "url" in result3:
            return  result3
          

# ai genrate data 
def AiGenratedProductData(product,product_scrape_array):

     ## genrated product obj using this product_scrape_array
     
     # dumy obj
     obj={
         **product,
         "desc":product_scrape_array[0]['description'],
         "price":product_scrape_array[0]['price'],
         "priceCurrency":product_scrape_array[0]['priceCurrency'],
         'AiRating':product_scrape_array[0]['ratingValue'],
         'image':product_scrape_array[0]['image'],
         'mrp':product_scrape_array[0]['mrp']
     }  
     
     return obj
    
# Health Check Route
@app.route('/health-check')
def index():
    return f'Server is up and running in port {port}'

# Route For Excel upload 
@app.route("/upload-excel", methods=["POST"])
def upload():
    
    product_obj=[]


    product_excel = request.files["product_excel"]
    dataframe1 = pd.read_excel(product_excel)
    
    # Convert DataFrame to a list of dictionaries
    data_as_list_of_dicts = dataframe1.to_dict(orient='records')
    
    for json_data in data_as_list_of_dicts:
       new_product_link=[]
       Array_product_link = json_data['similar_product'].split(',')
       for link in Array_product_link:
            new_product_link.append({
            "url":link,
            "platform":(link.split(".", 2)[1]).upper(),
            })
       product_obj.append(
            {**json_data,
            "similar_product":new_product_link
            }
       ) 
    try:
        product_data_store = database.product_import_data.insert_many(product_obj)
        if product_data_store.acknowledged:
            
            AiGenrated_product = []
            for product in product_obj:
                product_scrape_array=[]
                for product_url in product["similar_product"]:
                    
                    scrap_product =  productScrap(product_url)
                    
                    if scrap_product: 
                        product_scrape_array.append(scrap_product)
                        try:
                            db_response = database.scrap_product_data.insert_one(scrap_product) 
                        except:
                            return jsonify({'status':404,'msg':'data scrape error '}),404  
                    
                result = AiGenratedProductData(product,product_scrape_array)
                AiGenrated_product.append(result)             
            db_response = database.AiGenrated_product_data.insert_many(AiGenrated_product) 
            if db_response.acknowledged:
                return jsonify({'status':200,'msg':'data is successfully import' })
        
    except Exception as e:
        print(e)
        return jsonify({'status':404,'msg':'data importing failed'}),404      

# Route For corn job daily scrap dat and store to collection    
@app.route("/scraping-data", methods=["GET"])
def scrapingData():

    try:
        db_response = list(database.AiGenrated_product_data.find())
     
        
        for product in db_response:
            for product_url in product["similar_product"]:
                
                scrap_product =  productScrap(product_url)
                
                # if we run aigenrated function daily so all api hit are exhausted
                if scrap_product: 
                    updated_field={
                        **scrap_product,
                        "url":product_url["url"],
                        "updated_date":str(date.today())
                    }
                    
                try:
                    db_response = database.scrap_product_data.update_one({"url":product_url["url"]},{'$set' : updated_field}) 
                except Exception as e:
                    return jsonify({'status':404,'msg':e})   
                      
        return jsonify({'status':200,'msg':"collection has been updated successfully"})                     
                
    except Exception as e:
        return jsonify({'status':404,'msg':'upadtion data failed','error':e}), 404     

# Route for All PRoduct     
@app.route("/get-all-product", methods=["GET"])
def getAllProduct():
    try:
        product_data= database.AiGenrated_product_data.find()
        
        return  dumps(product_data),200
    
    except Exception as e:
          return jsonify({'status':404,"msg":"some error "}), 404
 
      
# Route fro product details
@app.route("/product/<string:product_id>", methods=["GET"])
def productDetails(product_id):
    try:
        product_data= database.AiGenrated_product_data.aggregate([
             {
                    '$match': {'_id': ObjectId(product_id)}
                },
                {
                    '$lookup': {
                        'from': 'scrap_product_data',
                        'localField': 'similar_product.url',
                        'foreignField': 'url',
                        'as': 'product_data'
                    }
                }
                
        ])
        
      
        

        
        return dumps(product_data),200
    
    except Exception as e:
          return jsonify({'status':404,"msg":"some error",'error':e}), 404

# Route for platform product analysis
@app.route("/price-update", methods=["GET"]) 
def priceStore():
    try:
        priceArray = []
        db_response  = list(database.scrap_product_data.find({},{'_id':1,'price':1,'url':1}))
        for obj in db_response:
            priceArray.append({
                'price':obj["price"],
                 'url':obj['url'],
                'date':str(date.today()),
                "scrap_product_id":obj['_id'],
            })  
    
        db_insertion = database.price_analysis.insert_many(priceArray)
        if db_insertion.acknowledged:
                return jsonify({'status':200,'msg':'price is successfully update ' })         
    except Exception as e:
        
        return jsonify({'status':404,"msg":"some error",'error':e}), 404                   


# Route to get price for  product analysis
@app.route("/price-get", methods=["POST"])  
def get_price():
    try:
        scrap_product_id = request.json['scrap_product_id']
        start_date = request.json['start_date']
        end_date = request.json['end_date'] or str(date.today())
       
        db_response = list(database.price_analysis.find({
            '$and' : [
             {'scrap_product_id':ObjectId(scrap_product_id)},   
            {'date': {'$gte':start_date}},
            {'date': {'$lte':end_date}}
            ]
        }))
        
        return dumps(db_response),200 
        
    except Exception as e:
         return jsonify({'status':404,"msg":"some error",'error':e}), 404           
    


if __name__ == '__main__':
    app.run(debug=True,port=port)
