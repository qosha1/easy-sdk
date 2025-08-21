Products Serializers
====================


CategorySerializer
------------------

Category serializer with hierarchical support

**File:** ``sample_projects/ecommerce_api/products/serializers.py``


**Inherits from:** serializers.ModelSerializer


Fields
^^^^^^


.. py:attribute:: children
   :type: 
   
   Children
   
   **Required**
   
   
   
   
   


.. py:attribute:: parent_name
   :type: 
   
   Parent Name
   
   **Required**
   
   
   
   
   






BrandSerializer
---------------

Brand serializer

**File:** ``sample_projects/ecommerce_api/products/serializers.py``


**Inherits from:** serializers.ModelSerializer


Fields
^^^^^^


.. py:attribute:: product_count
   :type: 
   
   Product Count
   
   **Required**
   
   
   
   
   






ProductImageSerializer
----------------------

Product image serializer

**File:** ``sample_projects/ecommerce_api/products/serializers.py``


**Inherits from:** serializers.ModelSerializer


Fields
^^^^^^






ProductListSerializer
---------------------

Product serializer for list views (minimal data)

**File:** ``sample_projects/ecommerce_api/products/serializers.py``


**Inherits from:** serializers.ModelSerializer


Fields
^^^^^^


.. py:attribute:: category_name
   :type: 
   
   Category Name
   
   **Required**
   
   
   
   
   


.. py:attribute:: brand_name
   :type: 
   
   Brand Name
   
   **Required**
   
   
   
   
   


.. py:attribute:: primary_image
   :type: 
   
   Primary Image
   
   **Required**
   
   
   
   
   


.. py:attribute:: current_price
   :type: 
   
   Current Price
   
   **Required**
   
   
   
   
   


.. py:attribute:: is_on_sale
   :type: 
   
   Is On Sale
   
   **Required**
   
   
   
   
   


.. py:attribute:: discount_percentage
   :type: 
   
   Discount Percentage
   
   **Required**
   
   
   
   
   






ProductDetailSerializer
-----------------------

Product serializer for detail views (complete data)

**File:** ``sample_projects/ecommerce_api/products/serializers.py``


**Inherits from:** serializers.ModelSerializer


Fields
^^^^^^


.. py:attribute:: category
   :type: 
   
   Category
   
   **Required**
   
   
   
   
   


.. py:attribute:: brand
   :type: 
   
   Brand
   
   **Required**
   
   
   
   
   


.. py:attribute:: images
   :type: 
   
   Images
   
   **Required**
   
   
   
   
   


.. py:attribute:: current_price
   :type: 
   
   Current Price
   
   **Required**
   
   
   
   
   


.. py:attribute:: is_on_sale
   :type: 
   
   Is On Sale
   
   **Required**
   
   
   
   
   


.. py:attribute:: discount_percentage
   :type: 
   
   Discount Percentage
   
   **Required**
   
   
   
   
   


.. py:attribute:: is_in_stock
   :type: 
   
   Is In Stock
   
   **Required**
   
   
   
   
   


.. py:attribute:: category_id
   :type: 
   
   Category Id
   
   **Required**
   
   
   
   
   


.. py:attribute:: brand_id
   :type: 
   
   Brand Id
   
   **Optional**
   
   
   
   
   






ProductCreateUpdateSerializer
-----------------------------

Product serializer for create/update operations

**File:** ``sample_projects/ecommerce_api/products/serializers.py``


**Inherits from:** serializers.ModelSerializer


Fields
^^^^^^


.. py:attribute:: images
   :type: 
   
   Images
   
   **Optional**
   
   
   
   
   






ProductSearchSerializer
-----------------------

Serializer for product search parameters

**File:** ``sample_projects/ecommerce_api/products/serializers.py``


**Inherits from:** serializers.Serializer


Fields
^^^^^^


.. py:attribute:: query
   :type: 
   
   Search query
   
   **Optional**
   
   
   
   
   


.. py:attribute:: category
   :type: 
   
   Category ID
   
   **Optional**
   
   
   
   
   


.. py:attribute:: brand
   :type: 
   
   Brand ID
   
   **Optional**
   
   
   
   
   


.. py:attribute:: min_price
   :type: 
   
   Minimum price
   
   **Optional**
   
   
   
   
   


.. py:attribute:: max_price
   :type: 
   
   Maximum price
   
   **Optional**
   
   
   
   
   


.. py:attribute:: in_stock_only
   :type: 
   
   Show only in-stock products
   
   **Required**
    (Default: ``False``)
   
   
   
   


.. py:attribute:: featured_only
   :type: 
   
   Show only featured products
   
   **Required**
    (Default: ``False``)
   
   
   
   


.. py:attribute:: on_sale_only
   :type: 
   
   Show only products on sale
   
   **Required**
    (Default: ``False``)
   
   
   
   


.. py:attribute:: status
   :type: 
   
   Product status
   
   **Required**
    (Default: ``active``)
   
   
   
   





