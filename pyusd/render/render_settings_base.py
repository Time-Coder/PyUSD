from ..typed import Typed
from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from typing import List
from ..dtypes import token
from ..gf import float4, int2
from ..relationship import Relationship
from ..common import SchemaKind


class RenderSettingsBase(Typed):
    """Abstract base class that defines render settings that
    can be specified on either a RenderSettings prim or a RenderProduct 
    prim."""
    schema_kind: SchemaKind = SchemaKind.AbstractTyped

    meta = {
        "customData": {
            "className": "SettingsBase"
        }
    }

    class AspectRatioConformPolicy(token):
        ExpandAperture = "expandAperture"
        CropAperture = "cropAperture"
        AdjustApertureWidth = "adjustApertureWidth"
        AdjustApertureHeight = "adjustApertureHeight"
        AdjustPixelAspectRatio = "adjustPixelAspectRatio"


    resolution: Attribute[int2] = Attribute(int2,
        uniform=True,
        doc=
        """The image pixel resolution, corresponding to the
        camera's screen window.
        """
    )

    pixelAspectRatio: Attribute[float] = Attribute(float,
        uniform=True,
        value=1.0,
        doc=
        """The aspect ratio (width/height) of image pixels..
        The default ratio 1.0 indicates square pixels.
        """
    )

    aspectRatioConformPolicy: Attribute[AspectRatioConformPolicy] = Attribute(AspectRatioConformPolicy,
        uniform=True,
        value="expandAperture",
        doc=
        """
        Indicates the policy to use to resolve an aspect
        ratio mismatch between the camera aperture and image settings.

        This policy allows a standard render setting to do something
        reasonable given varying camera inputs.

        The camera aperture aspect ratio is determined by the
        aperture atributes on the UsdGeomCamera.

        The image aspect ratio is determined by the resolution and
        pixelAspectRatio attributes in the render settings.

        - "expandAperture": if necessary, expand the aperture to
          fit the image, exposing additional scene content
        - "cropAperture": if necessary, crop the aperture to fit
          the image, cropping scene content
        - "adjustApertureWidth": if necessary, adjust aperture width
          to make its aspect ratio match the image
        - "adjustApertureHeight": if necessary, adjust aperture height
          to make its aspect ratio match the image
        - "adjustPixelAspectRatio": compute pixelAspectRatio to
          make the image exactly cover the aperture; disregards
          existing attribute value of pixelAspectRatio
        
        """
    )

    dataWindowNDC: Attribute[float4] = Attribute(float4,
        uniform=True,
        doc=
        """dataWindowNDC specifies the axis-aligned rectangular
        region in the adjusted aperture window within which the renderer
        should produce data.

        It is specified as (xmin, ymin, xmax, ymax) in normalized
        device coordinates, where the range 0 to 1 corresponds to the
        aperture.  (0,0) corresponds to the bottom-left
        corner and (1,1) corresponds to the upper-right corner.

        Specifying a window outside the unit square will produce
        overscan data. Specifying a window that does not cover the unit
        square will produce a cropped render.

        A pixel is included in the rendered result if the pixel
        center is contained by the data window.  This is consistent
        with standard rules used by polygon rasterization engines.
        \\ref UsdRenderRasterization

        The data window is expressed in NDC so that cropping and
        overscan may be resolution independent.  In interactive
        workflows, incremental cropping and resolution adjustment
        may be intermixed to isolate and examine parts of the scene.
        In compositing workflows, overscan may be used to support
        image post-processing kernels, and reduced-resolution proxy
        renders may be used for faster iteration.

        The dataWindow:ndc coordinate system references the
        aperture after any adjustments required by
        aspectRatioConformPolicy.
        
        """
    )

    instantaneousShutter: Attribute[bool] = Attribute(bool,
        uniform=True,
        value=False,
        doc=
        """Deprecated - use disableMotionBlur instead. Override
        the targeted _camera_'s _shutterClose_ to be equal to the
        value of its _shutterOpen_, to produce a zero-width shutter
        interval.  This gives us a convenient way to disable motion
        blur.
        """
    )

    disableMotionBlur: Attribute[bool] = Attribute(bool,
        uniform=True,
        value=False,
        doc=
        """Disable all motion blur by setting the shutter interval
        of the targeted camera to [0,0] - that is, take only one sample,
        namely at the current time code.
        """
    )

    disableDepthOfField: Attribute[bool] = Attribute(bool,
        uniform=True,
        value=False,
        doc=
        """Disable all depth of field by setting F-stop of the targeted
        camera to infinity.
        """
    )

    camera: Relationship = Relationship(
        doc=
        """The _camera_ relationship specifies the primary
        camera to use in a render.  It must target a UsdGeomCamera.
        """
    )
