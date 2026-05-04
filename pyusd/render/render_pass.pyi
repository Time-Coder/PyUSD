from ..typed import Typed
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import asset, namespace, string, token
from .collection import Collection

class RenderPass(Typed):
    @property
    def collection(self) -> Collection: ...

    @property
    def passType(self)->Attribute[token]:
        """A string used to categorize differently structured 
        or executed types of passes within a customized pipeline.

        For example, when multiple DCC's (e.g. Houdini, Katana, Nuke) 
        each compute and contribute different Products to a final result, 
        it may be clearest and most flexible to create a separate 
        RenderPass for each.
        """

    @passType.setter
    def passType(self, value:token)->None: ...

    @property
    def command(self)->Attribute[List[string]]:
        """The command to run in order to generate
        renders for this pass.  The job submission code can use
        this to properly send tasks to the job scheduling software
        that will generate products.

        The command can contain variables that will be substituted
        appropriately during submission, as seen in the example below 
        with {fileName}.

        For example:
        command[0] = "prman"
        command[1] = "-progress"
        command[2] = "-pixelvariance"
        command[3] = "-0.15"
        command[4] = "{fileName}" # the fileName property will be substituted
        """

    @command.setter
    def command(self, value:List[string])->None: ...

    @property
    def fileName(self)->Attribute[asset]:
        """The asset that contains the rendering prims or other 
        information needed to render this pass.
        """

    @fileName.setter
    def fileName(self, value:asset)->None: ...

    @property
    def renderSource(self)->Relationship:
        """The source prim to render from.  If _fileName_ is not present,
        the source is assumed to be a RenderSettings prim present in the current 
        Usd stage. If fileName is present, the source should be found in the
        file there. This relationship might target a string attribute on this 
        or another prim that identifies the appropriate object in the external 
        container.
 
        For example, for a Usd-backed pass, this would point to a RenderSettings
        prim.  Houdini passes would point to a Rop.  Nuke passes would point to 
        a write node.
        """

    @renderSource.setter
    def renderSource(self, value:Relationship)->None: ...

    @property
    def inputPasses(self)->Relationship:
        """The set of other Passes that this Pass depends on
        in order to be constructed properly.  For example, a Pass A
        may generate a texture, which is then used as an input to
        Pass B.
 
        By default, usdRender makes some assumptions about the
        relationship between this prim and the prims listed in inputPasses.
        Namely, when per-frame tasks are generated from these pass prims,
        usdRender will assume a one-to-one relationship between tasks
        that share their frame number.  Consider a pass named 'composite'
        whose _inputPasses_ targets a Pass prim named 'beauty`.  
        By default, each frame for 'composite' will depend on the 
        same frame from 'beauty':
        beauty.1 -> composite.1
        beauty.2 -> composite.2
        etc

        The consumer of this RenderPass graph of inputs will need to resolve
        the transitive dependencies.
        """

    @inputPasses.setter
    def inputPasses(self, value:Relationship)->None: ...

