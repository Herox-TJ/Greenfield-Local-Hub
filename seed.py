"""Run once to populate the database with sample data.
   Usage: python seed.py
   Credentials:
     Customer: customer@greenfield.com / Customer1!
     Producer: josh@greenvalley.com   / Producer1!
"""

from app import app, db
from model import User, Producer, Product, CartItem


def seed():
    with app.app_context():
        CartItem.query.delete()
        Product.query.delete()
        Producer.query.delete()
        User.query.delete()
        db.session.commit()

        #users
        customer = User(first_name='TJ', last_name='Swami',
                        email='customer@greenfield.com', role='customer')
        customer.set_password('Customer1!')

        prod_user = User(first_name='Josh', last_name='Green',
                         email='josh@greenvalley.com', role='producer')
        prod_user.set_password('Producer1!')

        db.session.add_all([customer, prod_user])
        db.session.flush()

        #producers
        PI = '/static/images/producers/'
        gvf = Producer(
            user_id=prod_user.id,
            name='Green Valley Farm', slug='green-valley-farm',
            description='Family-run organic farm specializing in seasonal vegetables and herbs.',
            location='Greenfield Valley, 5 miles from town center',
            image=PI + 'Green_valley_farm.jpg',
            farming_methods='Organic,No-till farming,Crop rotation',
            certifications='Organic Certified,Soil Association')
        so = Producer(
            name='Sunny Orchards', slug='sunny-orchards',
            description='Sustainable fruit orchard growing apples, pears, and stone fruits.',
            location='Hillside Road, 8 miles from town center',
            image=PI + 'Sunny_orchards.jpg',
            farming_methods='Integrated Pest Management,Heritage varieties',
            certifications='Red Tractor')
        mdc = Producer(
            name='Meadow Dairy Co.', slug='meadow-dairy-co',
            description='Grass-fed dairy farm producing milk, cheese, and butter.',
            location='Meadow Lane, 3 miles from town center',
            image=PI + 'Meadow_dairy_co.jpg',
            farming_methods='Grass-fed,Free-range,Rotational grazing',
            certifications='Pasture Promise,RSPCA Assured')
        hb = Producer(
            name='Heritage Bakehouse', slug='heritage-bakehouse',
            description='Artisan bakery using locally milled flour and traditional techniques.',
            location='Main Street, town center',
            image=PI + 'Heritage_bakehouse.jpg',
            farming_methods='Artisan,Locally sourced ingredients',
            certifications='Guild of Bakers')
        rp = Producer(
            name='Riverside Pastures', slug='riverside-pastures',
            description='Ethical livestock farm raising grass-fed beef and lamb.',
            location='River Road, 10 miles from town center',
            image=PI + 'Riverside_pastures.jpg',
            farming_methods='Grass-fed,Pasture-raised,Regenerative',
            certifications='Pasture for Life,Soil Association')

        db.session.add_all([gvf, so, mdc, hb, rp])
        db.session.flush()

        #products
        PI2 = '/static/images/products/'
        imgs = [
            'Organic_carrots.jpg',
            'Fresh_spinach.jpg',
            'Heritage_tomatoes.jpg',
            'Organic_potatoes.jpg',
            'Fresh_apples.jpg',
            'Ripe_pears.jpg',
            'Fresh_strawberries.jpg',
            'Whole_milk.jpg',
            'Farmhouse_cheddar.jpg',
            'Fresh_butter.jpg',
            'Sourdough_loaf.jpg',
            'Wholemeal_bread.jpg',
            'Grass-fed_beef_mince.jpg',
            'Lamb_chops.jpg',
        ]

        products = [
            Product(producer_id=gvf.id, name='Organic Carrots', slug='organic-carrots',
                    description='Sweet, crunchy carrots grown in rich organic soil.',
                    price=2.50, unit='1kg', stock=50, category='Vegetables', image=PI2+imgs[0]),
            Product(producer_id=gvf.id, name='Fresh Spinach', slug='fresh-spinach',
                    description='Tender baby spinach leaves, perfect for salads.',
                    price=3.00, unit='250g', stock=30, category='Vegetables', image=PI2+imgs[1]),
            Product(producer_id=gvf.id, name='Heritage Tomatoes', slug='heritage-tomatoes',
                    description='Mixed variety heritage tomatoes with rich flavour.',
                    price=4.50, unit='500g', stock=25, category='Vegetables', image=PI2+imgs[2]),
            Product(producer_id=gvf.id, name='Organic Potatoes', slug='organic-potatoes',
                    description='Versatile potatoes ideal for roasting or mashing.',
                    price=2.00, unit='2kg', stock=100, category='Vegetables', image=PI2+imgs[3]),
            Product(producer_id=so.id, name='Fresh Apples', slug='fresh-apples',
                    description='Crisp, juicy apples picked at peak ripeness.',
                    price=3.50, unit='1kg', stock=80, category='Fruits', image=PI2+imgs[4]),
            Product(producer_id=so.id, name='Ripe Pears', slug='ripe-pears',
                    description='Soft, sweet pears great for eating or cooking.',
                    price=4.00, unit='1kg', stock=60, category='Fruits', image=PI2+imgs[5]),
            Product(producer_id=so.id, name='Fresh Strawberries', slug='fresh-strawberries',
                    description='Sweet, juicy strawberries, freshly picked.',
                    price=5.00, unit='400g', stock=40, category='Fruits', image=PI2+imgs[6]),
            Product(producer_id=mdc.id, name='Whole Milk', slug='whole-milk',
                    description='Fresh whole milk from our grass-fed herd.',
                    price=1.80, unit='2L', stock=50, category='Dairy', image=PI2+imgs[7]),
            Product(producer_id=mdc.id, name='Farmhouse Cheddar', slug='farmhouse-cheddar',
                    description='Mature cheddar cheese aged for rich flavour.',
                    price=8.50, unit='400g', stock=30, category='Dairy', image=PI2+imgs[8]),
            Product(producer_id=mdc.id, name='Fresh Butter', slug='fresh-butter',
                    description='Churned butter made fresh from our dairy herd.',
                    price=3.20, unit='250g', stock=45, category='Dairy', image=PI2+imgs[9]),
            Product(producer_id=hb.id, name='Sourdough Loaf', slug='sourdough-loaf',
                    description='Traditional sourdough with a chewy crust.',
                    price=4.00, unit='800g', stock=20, category='Bakery', image=PI2+imgs[10]),
            Product(producer_id=hb.id, name='Wholemeal Bread', slug='wholemeal-bread',
                    description='Nutritious wholemeal bread with hearty texture.',
                    price=3.50, unit='750g', stock=25, category='Bakery', image=PI2+imgs[11]),
            Product(producer_id=rp.id, name='Grass-Fed Beef Mince', slug='grass-fed-beef-mince',
                    description='Lean grass-fed beef mince from free-range cattle.',
                    price=8.50, unit='500g', stock=35, category='Meat', image=PI2+imgs[12]),
            Product(producer_id=rp.id, name='Lamb Chops', slug='lamb-chops',
                    description='Tender lamb chops from pasture-raised animals.',
                    price=12.00, unit='500g', stock=20, category='Meat', image=PI2+imgs[13]),
        ]
        db.session.add_all(products)
        db.session.commit()

        print('Seed data created successfully.')
        print('  customer@greenfield.com / Customer1!')
        print('  josh@greenvalley.com    / Producer1!')


if __name__ == '__main__':
    seed() 