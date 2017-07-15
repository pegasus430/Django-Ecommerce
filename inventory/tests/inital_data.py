def create():
    StockLocation.objects.create(name='Knokke')
    StockLocation.objects.create(name='Gent')

    Relation.objects.create(business_name='Relation Name')

    Material.objects.create(
        sku='92GB2029',
        sku_supplier='AAADDB',
        name='Test Material',
        mat_type='FAB',
        cost_per_usage_unit=9.9,
        unit_usage='ME',
        unit_purchase='RO',
        unit_usage_in_purchase='30',
        est_delivery_time='3 weeks',
        supplier=Relation.objects.last(),
        )
    StockLocationItem.objects.create(
        location=StockLocation.objects.get(name='Knokke'),
        material=Material.objects.get(sku_supplier='AAADDB'),
        quantity_in_stock=200
        )

    Collection.objects.create(
        name='Collection Test',
        number='99',
        range_type='LUX',
        production_location=StockLocation.objects.get(name='Knokke')
        )

    Size.objects.create(
        full_size='Large',
        short_size='L',
        measurements='Dogs, length 30cm',
        )

    Colour.objects.create(
        name='Blue',
        code='BL',
        )

    UmbrellaProductModel.objects.create(
        name='Test Umbrella ProductModel',
        number='001',
        product_type='PL',
        )

    ProductModel.objects.create(
        umbrella_product_model=UmbrellaProductModel.objects.get(name='Test Umbrella ProductModel'),
        size=Size.objects.last(),
        )

    UmbrellaProduct.objects.create(
        name='Test Plad',
        collection=Collection.objects.last(),
        umbrella_product_model=UmbrellaProductModel.objects.last(),
        colour= Colour.objects.get(code='BL'),
        )

    UmbrellaProductBillOfMaterial.objects.create(
        material=Material.objects.last(),
        quantity_needed=0.9,
        umbrella_product=UmbrellaProduct.objects.last()
        )

    Product.objects.create(
        umbrella_product=UmbrellaProduct.objects.last(),
        product_model=ProductModel.objects.last()
        )
