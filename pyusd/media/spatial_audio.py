from pyusd.geom.xformable import Xformable
from ..attribute import Attribute
from typing import List
from ..dtypes import token
from ..dtypes import asset, double, timecode
from ..common import SchemaKind


class SpatialAudio(Xformable):
    """The SpatialAudio primitive defines basic properties for encoding 
    playback of an audio file or stream within a USD Stage. The SpatialAudio 
    schema derives from UsdGeomXformable since it can support full spatial 
    audio while also supporting non-spatial mono and stereo sounds. One or 
    more SpatialAudio prims can be placed anywhere in the namespace, though it 
    is advantageous to place truly spatial audio prims under/inside the models 
    from which the sound emanates, so that the audio prim need only be 
    transformed relative to the model, rather than copying its animation.

    \\section Usd_SpatialAudio_TimeScaling Timecode Attributes and Time Scaling
    \\a startTime and \\a endTime are \\ref SdfTimeCode "timecode" valued 
    attributes which gives them the special behavior that 
    \\ref SdfLayerOffset "layer offsets" affecting the layer in 
    which one of these values is authored are applied to the attribute's value 
    itself during value resolution. This allows audio playback to be kept in 
    sync with time sampled animation as the animation is affected by 
    \\ref SdfLayerOffset "layer offsets" in the composition. But this behavior 
    brings with it some interesting edge cases and caveats when it comes to 
    \\ref SdfLayerOffset "layer offsets" that include scale.

    ####  Layer Offsets do not affect Media Dilation
    Although authored layer offsets may have a time scale which can scale the
    duration between an authored \\a startTime and \\a endTime, we make no 
    attempt to infer any playback dilation of the actual audio media itself. 
    Given that \\a startTime and \\a endTime can be independently authored in 
    different layers with differing time scales, it is not possible, in general,
    to define an "original timeframe" from which we can compute a dilation to 
    composed stage-time. Even if we could compute a composed dilation this way,
    it would still be impossible to flatten a stage or layer stack into a single
    layer and still retain the composed audio dilation using this schema.
    """
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    class Auralmode(token):
        Spatial = "spatial"
        Nonspatial = "nonSpatial"

    class Playbackmode(token):
        Oncefromstart = "onceFromStart"
        Oncefromstarttoend = "onceFromStartToEnd"
        Loopfromstart = "loopFromStart"
        Loopfromstarttoend = "loopFromStartToEnd"
        Loopfromstage = "loopFromStage"


    filePath: Attribute[asset] = Attribute(asset,
        uniform=True,
        doc=
        """Path to the audio file.
        In general, the formats allowed for audio files is no more constrained 
        by USD than is image-type. As with images, however, usdz has stricter 
        requirements based on DMA and format support in browsers and consumer 
        devices. The allowed audio filetypes for usdz are M4A, MP3, WAV 
        (in order of preference).
        \\sa <a href="https://openusd.org/release/spec_usdz.html">Usdz Specification</a>
        
        """
    )

    auralMode: Attribute[Auralmode] = Attribute(Auralmode,
        uniform=True,
        value="spatial",
        doc=
        """Determines how audio should be played.
        Valid values are:
        - spatial: Play the audio in 3D space if the device can support spatial
          audio. if not, fall back to mono.
        - nonSpatial: Play the audio without regard to the SpatialAudio prim's 
          position. If the audio media contains any form of stereo or other 
          multi-channel sound, it is left to the application to determine 
          whether the listener's position should be taken into account. We 
          expect nonSpatial to be the choice for ambient sounds and music 
          sound-tracks.
        
        """
    )

    playbackMode: Attribute[Playbackmode] = Attribute(Playbackmode,
        uniform=True,
        value="onceFromStart",
        doc=
        """Along with \\a startTime and \\a endTime, determines when the 
        audio playback should start and stop during the stage's animation 
        playback and whether the audio should loop during its duration. 
        Valid values are:
        - onceFromStart: Play the audio once, starting at \\a startTime, 
          continuing until the audio completes.
        - onceFromStartToEnd: Play the audio once beginning at \\a startTime, 
          continuing until \\a endTime or until the audio completes, whichever 
          comes first.
        - loopFromStart: Start playing the audio at \\a startTime and continue 
          looping through to the stage's authored \\a endTimeCode.
        - loopFromStartToEnd: Start playing the audio at \\a startTime and 
          continue looping through, stopping the audio at \\a endTime.
        - loopFromStage: Start playing the audio at the stage's authored 
          \\a startTimeCode and continue looping through to the stage's authored 
          \\a endTimeCode. This can be useful for ambient sounds that should always 
          be active.
        
        """
    )

    startTime: Attribute[timecode] = Attribute(timecode,
        uniform=True,
        doc=
        """Expressed in the timeCodesPerSecond of the containing stage, 
        \\a startTime specifies when the audio stream will start playing during 
        animation playback. This value is ignored when \\a playbackMode is set 
        to loopFromStage as, in this mode, the audio will always start at the 
        stage's authored \\a startTimeCode.
        Note that \\a startTime is expressed as a timecode so that the stage can 
        properly apply layer offsets when resolving its value. See 
        \\ref Usd_SpatialAudio_TimeScaling for more details and caveats.
        
        """
    )

    endTime: Attribute[timecode] = Attribute(timecode,
        uniform=True,
        doc=
        """Expressed in the timeCodesPerSecond of the containing stage, 
        \\a endTime specifies when the audio stream will cease playing during 
        animation playback if the length of the referenced audio clip is 
        longer than desired. This only applies if \\a playbackMode is set to 
        onceFromStartToEnd or loopFromStartToEnd, otherwise the \\a endTimeCode 
        of the stage is used instead of \\a endTime.
        If \\a endTime is less than \\a startTime, it is expected that the audio 
        will instead be played from \\a endTime to \\a startTime.
        Note that \\a endTime is expressed as a timecode so that the stage can 
        properly apply layer offsets when resolving its value.
        See \\ref Usd_SpatialAudio_TimeScaling for more details and caveats.
        
        """
    )

    mediaOffset: Attribute[double] = Attribute(double,
        uniform=True,
        doc=
        """Expressed in seconds, \\a mediaOffset specifies the offset from 
        the referenced audio file's beginning at which we should begin playback 
        when stage playback reaches the time that prim's audio should start.
        If the prim's \\a playbackMode is a looping mode, \\a mediaOffset is 
        applied only to the first run-through of the audio clip; the second and 
        all other loops begin from the start of the audio clip.
        
        """
    )

    gain: Attribute[double] = Attribute(double,
        value=1.0,
        doc=
        """Multiplier on the incoming audio signal. A value of 0 "mutes" 
        the signal. Negative values will be clamped to 0. 
        
        """
    )
