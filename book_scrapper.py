from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq   # when use uReq to get request
import requests
import re
import pandas as pd
#import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# import requests
# result = requests.get(main_url)
#
# print("result = ",result)
# #print(result.text)
#
# #The result is quite messy! Let’s make this more readable:
# soup = BeautifulSoup(result.text, 'html.parser')
# #soup
# print(soup.prettify())  #The function prettify() makes the HTML more readable

#function to get only html parser of any link
def send_get_req(url_link):
    result = requests.get(url_link)

    ##alternative way to get response
    # uClient = uReq(my_url)
    # page_html = uClient.read()
    # uClient.close()

    response = soup(result.text, "html.parser")
    return response


#function to get review section in the all_reviews page
def review_section(link):
    review_soup = send_get_req(link)
    review_page = review_soup.findAll("div",{"class" : "_2m08jR"})[0].div.div
    # print(review_page)

    review_section  = review_page.findAll("div",{"class" : "ooJZfD _2oZ8XT col-9-12"})
    if len(review_section[0].div.findAll("div", {"class" : "_3gijNv col-12-12"})) != 0:  # review section has analysis bar which has _3gijNv col-12-12 div class
        review_contents = review_section[0].findAll("div", {"class" : "_3gijNv col-12-12"})[1:]
    else:
        print("hhhh")
        review_contents = review_section[0].findAll("div", {"class": "_3gijNv col-12-12"})

    return review_contents


# total number of pages from all_reviews page
def total_pages(review_content_section):
    next_button_text2 = review_content_section[-1].div.div.span.text
    # print(next_button_text2)
    no_of_pages = int(next_button_text2.split("of ")[1])
    return no_of_pages


# total number of reviews from main product page
def no_of_reviews(review_content_section):
    try:
        review_quantity_text = review_content_section.div.findAll("span",{"class" : "_38sUEc _1je6zX"})[0]
        print("review_quantity_text",review_quantity_text)
        review_quantity = review_quantity_text.text.split("and ")[1].split(" ")[0]
        #changing number format from 3,234 to 3234
        review_quantity = int("".join(review_quantity.split(",")))
        return review_quantity
    except:
        print("eseche")
        review_quantity_text = review_content_section.findAll("div", {"class": "row _1Ahy2t _2aFisS"})[0]
        print("review_quantity_text",review_quantity_text)
        review_quantity_text = review_quantity_text.div.div.div.div.findAll("div", {"class": "row _2yc1Qo"})[-1].div.span
        review_quantity = review_quantity_text.text.split(" ")[0]
        # changing number format from 3,234 to 3234
        review_quantity = int("".join(review_quantity.split(",")))
        return review_quantity


#information_gathering
def information_extraction(info_section):
    try:
        rating = info_section.findAll("div", {"class": re.compile("hGSR34 E_uFuv")})[0].text
        print(rating)
    except:
        rating = "NIL"

    # description
    try:
        description = info_section.findAll("p", {"class": re.compile("_2xg6Ul")})[0].get_text(strip=True, separator='.')
    except:
        description = "NIL"

    # review
    try:
        try:
            try:
                review = info_section.findAll("div", {"class": "row"})[1].div.div.div.get_text(strip=True, separator='.')
            except:
                review = info_section.findAll("div", {"class": "row"})[0].div.div.div.get_text(strip=True, separator='.')
        except:
            review = info_section.findAll("div", {"class": re.compile("_2t8wE0")})[0].get_text(strip=True, separator='.')
    except:
        review = "NIL"

    # date info
    date_info = info_section.findAll("div", {"class": "row _2pclJg"})
    try:
        date = date_info[0].div.findAll("p", {"class": "_3LYOAd"})[-1].text
    except:
        date = "NIL"

    return [rating,description,review,date]


#function to get scrapped rating,descriptions,reviews for each page of total pages
def scrapped_reviews_data(review_content_section):
    total_review = 0
    all_reviews = []
    all_ratings = []
    all_descriptions = []
    all_dates = []
    for review in review_content_section[1:(len(review_content_section) - 1)]:
        #print(review)
        all_info = review.div.div.div
        print(all_info)
        #rating and description and review info
        #rating
        rating, description, review, date = information_extraction(all_info)

        all_ratings.append(rating)
        all_descriptions.append(description)
        all_reviews.append(review)
        all_dates.append(date)
        total_review = total_review + 1

    return [total_review,all_ratings,all_descriptions,all_reviews,all_dates]

# def info_extractor_multiple_pages(url):
#         review_link = url
#         review_contents_page_wise = review_section(review_link)
#         review_no, ratings_page_wise, descriptions_page_wise, reviews_page_wise, dates_page_wise = scrapped_reviews_data(review_contents_page_wise)
#
#         rating_list.extend(ratings_page_wise)
#         description_list.extend(descriptions_page_wise)
#         review_list.extend(reviews_page_wise)
#         date_list.extend(dates_page_wise)
#         return [rating_list,description_list,review_list,date_list]


#start searching and parsing informations

# def scrapeer_for_multiple_all_reviews(review_page_no):
#     review_count = 0
#     #for i in range(review_page_no):
#     if review_count <= given_review_no and review_count <= total_review:
#         print(review_count)
#         review_link = review_first_page_link + '&page=' + str((i + 1))
#         print(review_link)
#         review_contents_page_wise = review_section(review_link)
#         review_no, ratings_page_wise, descriptions_page_wise, reviews_page_wise, dates_page_wise = scrapped_reviews_data(
#             review_contents_page_wise)
#
#         review_count = review_count + review_no
#     else:
#         break
#     return [ratings_page_wise, descriptions_page_wise, reviews_page_wise, dates_page_wise]


def scrapper(product_page_link,given_review_no):
    # lists for all lists
    rating_list = []
    description_list = []
    review_list = []
    date_list = []
    # given count of reviews
    #given_review_no = 5000
    review_count = 0

    # try:  #when reviews are present
    product_soup = send_get_req(product_page_link)
    print(product_soup)
    # containers_product = product_soup.findAll("div", {"class": "_1HmYoV _35HD7C col-8-12"})[0].findAll("div", {"class": "_1HmYoV _35HD7C"})
    # # print(containers_product)
    #
    # containers_product1 = containers_product[0].findAll("div", {"class": "bhgxx2 col-12-12"})
    # print(len(containers_product1))
    try:  # sometimes review section of main page is present in 3rd last 'bhgxx2 col-12-12' div
        # target_container = containers_product1[len(containers_product1) - 3]

        target_container1 = product_soup.findAll("div", {"class": re.compile("col _39LH-M")})[0]
        total_review = no_of_reviews(target_container1)
        print("total_review", total_review)
    except:  # sometimes review section of main page is present in 2nd last 'bhgxx2 col-12-12' div
        # target_container = containers_product1[len(containers_product1) - 2]

        target_container1 = product_soup.findAll("div", {"class": re.compile("col _39LH-M")})[0]
        total_review = no_of_reviews(target_container1)
        print("total_review", total_review)

    try:  # if all reviews button is avaiable
        print("all_reviews button is avaiable")
        list_of_all_reviews_link = target_container1.findAll("a", href=re.compile("product-reviews"))
        print(list_of_all_reviews_link)
        if len(list_of_all_reviews_link) > 1:
            link_break_down_list = product_page_link.split("/")
            print(link_break_down_list)
            link_break_down_list[4] = "product-reviews"
            review_first_page_link = "/".join(link_break_down_list).strip()
        else:
            print("eseche")
            print(url + target_container1.findAll("a", href=re.compile("product-reviews"))[0]['href'][1:])
            review_first_page_link = url + target_container1.findAll("a", href=re.compile("product-reviews"))[0]['href'][1:]
            print(review_first_page_link)
        print(review_first_page_link)

        # review content section for each page link
        review_contents = review_section(review_first_page_link)

        try:
            print("total number of pages is available")
            # total review pages number
            total_review_pages = total_pages(review_contents)
            print("total_review_pages", total_review_pages)


            for i in range(total_review_pages):
                if review_count <= given_review_no and review_count <= total_review:
                    print(review_count)
                    review_link = review_first_page_link + '&page=' + str((i + 1))
                    print(review_link)
                    review_contents_page_wise = review_section(review_link)
                    review_no, ratings_page_wise, descriptions_page_wise, reviews_page_wise, dates_page_wise = scrapped_reviews_data(
                        review_contents_page_wise)

                    review_count = review_count + review_no
                    rating_list.extend(ratings_page_wise)
                    description_list.extend(descriptions_page_wise)
                    review_list.extend(reviews_page_wise)
                    date_list.extend(dates_page_wise)
                else:
                    break

            # processes1 = []
            # with ThreadPoolExecutor(max_workers=10) as executor:
            #     for page_no in range(total_review_pages):
            #         processes1.append(executor.submit(result_from_review, review))
            #
            # for task in as_completed(processes):
            #     print("result", task.result())
            #     spam_list.append(task.result()[0])
            #     emotion_list.append(task.result()[1])
            #     suggestion_review_text_list.append(task.result()[2])

        except:
            print("only one page is avialable in all_reviews page")
            while True:
                review_contents_page_wise = review_section(review_first_page_link)
                review_no, ratings_page_wise, descriptions_page_wise, reviews_page_wise, dates_page_wise = scrapped_reviews_data(
                    review_contents_page_wise)
                review_count = review_count + review_no
                rating_list.extend(ratings_page_wise)
                description_list.extend(descriptions_page_wise)
                review_list.extend(reviews_page_wise)
                date_list.extend(dates_page_wise)
                if review_count > given_review_no or review_count > total_review:
                    print("no more reviews to scrap")
                    break

    except:  # if all reviews button is not avaiable i.e only one page of comments
        print("only one page of reviews in main page")
        review_section_main_page_container = target_container1.findAll("div", {"class": re.compile("_2aFisS")})[0]
        review_sections_list = review_section_main_page_container.findAll("div",
                                                                          {"class": "_3nrCtb" or "_3nrCtb QPvkn6"})
        for each_section in review_sections_list:
            section_info = each_section.div.div
            # section = section_info.findAll("div",{"class" : "row"})
            # if len(section) < 2: # only one 'row' div section
            #     # rating and review section
            #     #rating
            #     try:
            #         rating = section.div.div.text
            #     except:
            #         rating = "NIL"
            #
            #     # review
            #     try:
            #         review = section.div.div.div.text
            #     except:
            #         review = "NIL"
            #
            #     #description
            #     description = "NIL"
            #
            #     #date
            #     try:
            #         date = each_section.div.div.findALL("div",{"class" : "row _2pclJg"})[0].div.findAll("p",{"class": "_3LYOAd"})[-1].text
            #     except:
            #         date = "NIL"
            #
            # else:
            # gathering rating information
            rating, description, review, date = information_extraction(section_info)

            rating_list.append(rating)
            description_list.append(description)
            review_list.append(review)
            date_list.append(date)

    dict = {"Description": description_list, "Rating": rating_list, "Review": review_list, "Date": date_list}
    dataset = pd.DataFrame(dict).iloc[:given_review_no, :]
    return dataset

    # except:
    #     print("no review available")
    #     dataset = pd.DataFrame({})
    # return dataset


url = "https://www.flipkart.com/"
#
# #GIVE NAME OF SEARCH ITEM
search_item = "book"
my_url = url+ "search?q=" + re.sub(" ","-",search_item)  #changing the search string

print(my_url)

page_soup = send_get_req(my_url)

# container = page_soup.findAll("div", { "class": "_1YokD2 _3Mn1Gg"})[0].findAll("div" , {"class" : "_1HmYoV _35HD7C"})[1]
container = page_soup.findAll("div", {"class": ""})
first_product_link = url + page_soup.findAll("div",{"class" : "_2rpwqI"})[0].div.div.div.a["href"][1:]
print(first_product_link)

#OR GIVE PRODUCT PAGE NAMEhttps://www.flipkart.com/redmi-note-7-pro-neptune-bl
# first_product_link = "https://www.flipkart.com/flipkart-smartbuy-back-cover-mi-redmi-note-3/p/itmf9rd8exm7yece?pid=ACCF9RD3NFDNZQZE&lid=LSTACCF9RD3NFDNZQZECLE4LA&marketplace=FLIPKART&srno=s_1_1&otracker=search&fm=organic&iid=2156718f-88fa-4a94-9ac3-68b6fe554a9c.ACCF9RD3NFDNZQZE.SEARCH&ssid=l7pqkqlx400000001595918057122&qH=d4faef21f2b35ea2"
# print(target_container)

dataset = scrapper(first_product_link,50)
dataset.to_csv("products_data.csv")