from ..api_schema_base import APISchemaBase


class AssetPreviewsAPI(APISchemaBase):
    """AssetPreviewsAPI is the interface for authoring and accessing 
        precomputed, lightweight previews of assets.  It is an applied schema, 
        which means that an arbitrary number of prims on a stage can have the schema 
        applied and therefore can contain previews; however, to access a stage's 
        "default" previews, one consults 
        the stage's `defaultPrim`.
        
        AssetPreviewsAPI supports the following kinds of previews:
        - **thumbnails** : a set of pre-rendered images of the asset.  There is no 
          prescribed size for thumbnail images, but care should be taken to ensure
          their inclusion does not substantially increase the overall size of an
          asset, as, for example, when packaged into USDZ.
        
        Although the UsdMediaAssetPreviewsAPI class can be used to interrogate any
        prim, no query in the API will succeed unless the schema has been applied
        to the prim.  This schema deals only with asset paths, and clients wishing
        to directly consume the returned data must do so by retrieving an ArAsset
        from the session's ArAssetResolver.
        
        The schema defines no properties or metadata fallback values.  Rather, 
        Asset Previews are encoded as part of a prim's `assetInfo` metadata.  A 
        default thumbnail image would look like:
        ```
    1.    assetInfo = {
    2.      dictionary previews = {
    3.          dictionary thumbnails = {
    4.              dictionary default = {
    5.                  asset defaultImage = @chair_thumb.jpg@
    6.              }
    7.          }
    8.      }
    9.    }
        ```
    
        
    """

