Products Serializers
====================


CategorySerializer
------------------

Category serializer with hierarchical support

**File:** ``products/serializers.py``


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
   
   
   
   
   




Example Usage
^^^^^^^^^^^^^

Python Usage:

.. code-block:: python
   :caption: Creating Category instance

   from products.serializers import CategorySerializer
   
   # Create serializer instance
   serializer = CategorySerializer(data=request.data)
   if serializer.is_valid():
       instance = serializer.save()
   else:
       print(serializer.errors)

JavaScript/TypeScript Usage:

.. code-block:: javascript
   :caption: Frontend API Call

   // Fetch category data
   const response = await fetch('/api/products/category/', {
     method: 'GET',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${token}`
     }
   });
   const data = await response.json();

cURL Example:

.. code-block:: bash
   :caption: Command Line API Call

   curl -X GET "http://localhost:8000/api/products/category/"      -H "Accept: application/json"      -H "Authorization: Bearer YOUR_TOKEN"




BrandSerializer
---------------

Brand serializer

**File:** ``products/serializers.py``


**Inherits from:** serializers.ModelSerializer


Fields
^^^^^^


.. py:attribute:: product_count
   :type: 
   
   Product Count
   
   **Required**
   
   
   
   
   




Example Usage
^^^^^^^^^^^^^

Python Usage:

.. code-block:: python
   :caption: Creating Brand instance

   from products.serializers import BrandSerializer
   
   # Create serializer instance
   serializer = BrandSerializer(data=request.data)
   if serializer.is_valid():
       instance = serializer.save()
   else:
       print(serializer.errors)

JavaScript/TypeScript Usage:

.. code-block:: javascript
   :caption: Frontend API Call

   // Fetch brand data
   const response = await fetch('/api/products/brand/', {
     method: 'GET',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${token}`
     }
   });
   const data = await response.json();

cURL Example:

.. code-block:: bash
   :caption: Command Line API Call

   curl -X GET "http://localhost:8000/api/products/brand/"      -H "Accept: application/json"      -H "Authorization: Bearer YOUR_TOKEN"




ProductImageSerializer
----------------------

Product image serializer

**File:** ``products/serializers.py``


**Inherits from:** serializers.ModelSerializer


Fields
^^^^^^




Example Usage
^^^^^^^^^^^^^

Python Usage:

.. code-block:: python
   :caption: Creating ProductImage instance

   from products.serializers import ProductImageSerializer
   
   # Create serializer instance
   serializer = ProductImageSerializer(data=request.data)
   if serializer.is_valid():
       instance = serializer.save()
   else:
       print(serializer.errors)

JavaScript/TypeScript Usage:

.. code-block:: javascript
   :caption: Frontend API Call

   // Fetch productimage data
   const response = await fetch('/api/products/productimage/', {
     method: 'GET',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${token}`
     }
   });
   const data = await response.json();

cURL Example:

.. code-block:: bash
   :caption: Command Line API Call

   curl -X GET "http://localhost:8000/api/products/productimage/"      -H "Accept: application/json"      -H "Authorization: Bearer YOUR_TOKEN"




ProductListSerializer
---------------------

Product serializer for list views (minimal data)

**File:** ``products/serializers.py``


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
   
   
   
   
   




Example Usage
^^^^^^^^^^^^^

Python Usage:

.. code-block:: python
   :caption: Creating ProductList instance

   from products.serializers import ProductListSerializer
   
   # Create serializer instance
   serializer = ProductListSerializer(data=request.data)
   if serializer.is_valid():
       instance = serializer.save()
   else:
       print(serializer.errors)

JavaScript/TypeScript Usage:

.. code-block:: javascript
   :caption: Frontend API Call

   // Fetch productlist data
   const response = await fetch('/api/products/productlist/', {
     method: 'GET',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${token}`
     }
   });
   const data = await response.json();

cURL Example:

.. code-block:: bash
   :caption: Command Line API Call

   curl -X GET "http://localhost:8000/api/products/productlist/"      -H "Accept: application/json"      -H "Authorization: Bearer YOUR_TOKEN"




ProductDetailSerializer
-----------------------

Product serializer for detail views (complete data)

**File:** ``products/serializers.py``


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
   
   
   
   
   




Example Usage
^^^^^^^^^^^^^

Python Usage:

.. code-block:: python
   :caption: Creating ProductDetail instance

   from products.serializers import ProductDetailSerializer
   
   # Create serializer instance
   serializer = ProductDetailSerializer(data=request.data)
   if serializer.is_valid():
       instance = serializer.save()
   else:
       print(serializer.errors)

JavaScript/TypeScript Usage:

.. code-block:: javascript
   :caption: Frontend API Call

   // Fetch productdetail data
   const response = await fetch('/api/products/productdetail/', {
     method: 'GET',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${token}`
     }
   });
   const data = await response.json();

cURL Example:

.. code-block:: bash
   :caption: Command Line API Call

   curl -X GET "http://localhost:8000/api/products/productdetail/"      -H "Accept: application/json"      -H "Authorization: Bearer YOUR_TOKEN"




ProductCreateUpdateSerializer
-----------------------------

Product serializer for create/update operations

**File:** ``products/serializers.py``


**Inherits from:** serializers.ModelSerializer


Fields
^^^^^^


.. py:attribute:: images
   :type: 
   
   Images
   
   **Optional**
   
   
   
   
   




Example Usage
^^^^^^^^^^^^^

Python Usage:

.. code-block:: python
   :caption: Creating ProductCreateUpdate instance

   from products.serializers import ProductCreateUpdateSerializer
   
   # Create serializer instance
   serializer = ProductCreateUpdateSerializer(data=request.data)
   if serializer.is_valid():
       instance = serializer.save()
   else:
       print(serializer.errors)

JavaScript/TypeScript Usage:

.. code-block:: javascript
   :caption: Frontend API Call

   // Fetch productcreateupdate data
   const response = await fetch('/api/products/productcreateupdate/', {
     method: 'GET',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${token}`
     }
   });
   const data = await response.json();

cURL Example:

.. code-block:: bash
   :caption: Command Line API Call

   curl -X GET "http://localhost:8000/api/products/productcreateupdate/"      -H "Accept: application/json"      -H "Authorization: Bearer YOUR_TOKEN"




ProductSearchSerializer
-----------------------

Serializer for product search parameters

**File:** ``products/serializers.py``


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
   
   
   
   




Example Usage
^^^^^^^^^^^^^

Python Usage:

.. code-block:: python
   :caption: Creating ProductSearch instance

   from products.serializers import ProductSearchSerializer
   
   # Create serializer instance
   serializer = ProductSearchSerializer(data=request.data)
   if serializer.is_valid():
       instance = serializer.save()
   else:
       print(serializer.errors)

JavaScript/TypeScript Usage:

.. code-block:: javascript
   :caption: Frontend API Call

   // Fetch productsearch data
   const response = await fetch('/api/products/productsearch/', {
     method: 'GET',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${token}`
     }
   });
   const data = await response.json();

cURL Example:

.. code-block:: bash
   :caption: Command Line API Call

   curl -X GET "http://localhost:8000/api/products/productsearch/"      -H "Accept: application/json"      -H "Authorization: Bearer YOUR_TOKEN"



