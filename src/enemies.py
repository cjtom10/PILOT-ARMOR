from re import A, S
from panda3d.bullet import *
from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.actor.Actor import Actor
from direct.interval.LerpInterval import *
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import Sequence, Parallel, Func, Wait
import random
import math
from lvl import HealthBar
class Enemy():
    def __init__(self, world, parentnode, actor, startpos,posture,hbshader,spawnpoint,initState,  name ):
        self.active = False
        self.health = .01
        self.chargeAMT = 0.98
        self.posture = posture
        self.world = world
        self.parentnode = parentnode
        self.name = name
        self.spawnPoint = spawnpoint
        
      

        self.isAttacking =False
        self.deflected = False
        self.model = actor
        self.capsule = BulletCapsuleShape(1,2)
        self.controller =BulletCharacterControllerNode(self.capsule,0.4, name)
        self.speed = 0
        

        self.NP =parentnode.attachNewNode(self.controller)
        self.NP.setCollideMask(BitMask32.bit(1))
        self.world.attachCharacter(self.controller)

        self.model.reparentTo(self.NP)
        self.model.setZ(-2)

        self.d2p = int
        # self.parrypos = parrypos.find('enemyparrypos')
        # self.parrypos.setCompass(self.NP)
        # self.anim = self.model.getCurrentAnim()
        # self.frame =self.model.getCurrentFrame()
        self.solidsCleared = False
        self.isHit = False
        self.hasHit=False
        self.startpos = startpos
        self.NP.setPos(self.startpos)

        self.lookTarget = Point3(0,0,0)### target to lookat player
        self.moveTarget = Point3(0,0,0)### move to here
        
        self.trackPlayer = True

        self.atkNode = NodePath(CollisionNode(f'{self.name}attack'))
        self.atkorder = 0
        self.atx = {0:'slash',1:'slash2'}#diff atacks stored here

        self.seq = None

        self.inRange = False

        # self.pdodgecheck = NodePath(BulletRigidBodynode(f'{self.name}pdodge'))
        # self.pdodgecheck.node().setKinematic(True)
        # self.pdodgecheck.node().addShape)

        # self.world.attachRigidBody(self.pdodgecheck.node())
        self.currentBehavior =  initState

        self.attached=False
        ###TODO Attach hb to joint instead of being arbitratry
        self.Hitbox=[]

        # self.currentBehavior = None
        self.behaviors = {1:'run',
                          2: 'idle',
                          3:'attack',4:'attack',5:'attack'}
#######healthbar
        self.healthbar = HealthBar(pos=(-1, 1, .9, 1.1))
        # self.healthbar.postureBar(pos = (-1,1,0.6, .8))
        self.healthbar.setCompass(base.camera)
        self.healthbar.reparentTo(self.NP)
        self.healthbar.setZ(3)
        


        # self.hb(name)
        # self.hbSetup()
    def hbSetup(self):
        # pass
        #placeholder - need to attach hbs to bones
        chestHB= CollisionCapsule(0, .5, 4, 0, 0, 0, .5)
        self.HB = self.NP.attachNewNode(CollisionNode(f'{self.name}hb'))
        self.HB.node().addSolid(chestHB)
        self.HB.setY(-.2)
        self.HB.show()
    # def resetPosture(self):
    #     self.posture = posture
    def update(self):#, task):
        # print('posture', self.posture,'attackiing?', self.isAttacking)
        # if self.active == False:
        #     return\

        #finisher event
        # if self.posture <=0:
        #     self.currentBehavior = "stunned", accept finisher

        if self.currentBehavior==None:
            self.randomizebehavior()
        self.anim = self.model.getCurrentAnim()
        self.frame =self.model.getCurrentFrame()

        self.d2p = (self.NP.getPos()-self.moveTarget).length()
        if self.d2p <3: 
            self.inRange = True
        if self.d2p >3:
            self.inRange = False # block out runnoing if iun range

        #

        self.d2p = (self.NP.getPos(render) - self.moveTarget).length()
        if self.trackPlayer==True:
            # self.NP.lookAt(self.lookTarget)
            self.tracktarget()
    #   ######FIX THIS LATER
        if self.deflected ==True:
            return #task.cont
    ########
        # if self.isAttacking!=True:
        #     self.atkNode.node().clearSolids()
        #     self.attached=False
        
        if self.isAttacking==True and self.frame!=None:
            if self.frame>15:
                self.isAttacking=False
            else:
                return #task.cont
 
        processaction={
                            'idle': self.idle,
                            'run': self.processRun,
                            'attack': self.processAttack, 
                            'deflected': self.processDeflect,
                            'stunned': self.isStunned,
                            'charging': self.processCharge,
                          
            }
        if self.active ==True and self.currentBehavior!=None:
            processaction[self.currentBehavior]()
########healthbar update
        self.healthbar.setPosture(self.posture)
        if self.health <1:
        
            self.healthbar.setHealth(self.health)
        
        if self.posture>.01:
            self.resetPosture()
        self.controller.setLinearMovement(self.speed, False)
        return #task.cont
    def randomizebehavior(self):#, task):
        """2 behaivors, when not in attack range and when in attacl range"""
        # print('randopmzia', self.d2p)
        self.d2p= (self.NP.getPos() - self.lookTarget).length()
        # if self.d2p>3:
        if self.inRange == False:
            num = random.randint(1,2)
        if self.inRange ==True:
            num = random.randint(2,5)
        #     print('1 to 2')
        # elif self.d2p<3:
        #     num = random.randint(2,5)
        #     print('2 to 5')
        self.currentBehavior = self.behaviors.get(num)
        # return task.again

        
    def resetPosture(self):
        #change this to descreete values
        self.posture -=.001
        if self.posture > 1:
            self.posture = 0.999
            print('stun!')

    def die(self):
        print('dead')
        # self.world.removeRigidBody(self.capsule.node())
        self.NP.detachNode()
        taskMgr.remove(self.update)
        #includes model, hb, character controller node, update task
    def atkhb(self,parent,shape ):

        # self.blade = self.model.expose_joint(None, 'modelRoot', 'blade')
        self.attached=True
        # self.atkNode = NodePath(CollisionNode(f'{self.name}attack'))
        # HitB = CollisionCapsule((0, 0, 0), (0, 2.5, 0), .3)
        self.atkNode.reparentTo(parent)
        self.atkNode.node().addSolid(shape)
        self.atkNode.show()
    def processAttack(self):
        self.speed = 0
        # print('qattacking state', self.d2p)
        if  self.d2p <10 and self.d2p > 5:
            print('strafe')
            self.speed = render.getRelativeVector(self.model, (5,0,0))
            return

        if self.isAttacking ==True:
            return
        else:
            self.doAttack(anim=self.atx[self.atkorder])

    def doAttack(self,anim='slash', limit = 2):#, limit=2):#, task):
        """limit is the max a mount of combos"""
        self.atkorder+=1
        self.isAttacking=True
        # if (self.anim!='slash'):
        #     self.model.play('slash')
        # if self.attached==False:
        def attach():
            if self.attached==False:
                self.atkhb(self.model.exposeJoint(None, "modelRoot", "swordpos"),
                   CollisionCapsule((0, 0, 0), (0, 2.5, 0), .3))
        def detach():
                self.atkNode.node().clearSolids()
                self.attached=False
        def endatk():
            self.isAttacking=False
            self.hasHit = False
            
            if self.atkorder>=limit:# wensures that each attack is 2 attacks
                self.atkorder=0
                # self.currentBehavior = None

        atta = Func(attach)
        HBend=Func(detach)
        end =Func(endatk)
        s1 = self.model.actorInterval(anim,loop = 0, startFrame=0, endFrame = 6)
        s2 = self.model.actorInterval(anim,loop = 0, startFrame=7, endFrame = 18)
        s3 = self.model.actorInterval(anim,loop = 0, startFrame=19, endFrame = 25)
        
        #if self.atkorder==0:#first attack
        if self.seq!=None:
            if self.seq.isPlaying():
                self.seq.pause()
        self.seq = Sequence(s1, Parallel(s2, atta),Parallel(s3,HBend), end)

        self.seq.start()
        # return task.again
    def processDeflect(self):
        #anim should only playy for stuyn state
        # if self.seq.isPlaying():
        #         self.seq.pause()
        # self.posture+=.3
        p = Func(self.seq.pause)#### add vfx here later
        r = Func(self.seq.resume)
        self.isAttacking =False
        self.attached = False
        self.atkNode.node().clearSolids()

        # atkpause = Sequence(p, Wait(.1), r)
        # if atkpause.isPlaying():
        #     return
        # else:
        #     atkpause.start()
        # print(self.frame)
        ##should go into either attack or stuned

    def attachWeapon(self,weapon, parent):
        weapon.reparentTo(parent)

    def tracktarget(self):
        a = self.model.getX(render) - self.lookTarget.x
        b = self.model.getY(render) - self.lookTarget.y

        h = math.atan2(a,-b )
        angle = math.degrees(h) 

        # self.closest = closest
        self.model.setH(render, angle)
        #model faces player indpendent of capsule

        # self.NP.lookAt(self.lookTarget)
        # self.Np.setH(render, 0)
        # self.NP.setP(0)

        # dir = self.NP.getQuat().getForward() * 3
        # self.controller.setLinearMovement(dir, False)
        # # print(dis)

        # if dis<3 and self.isAttacking!=True:
        #     self.attack()

    def processCharge(self):
        # print(self.name, 'chargingup hhnnnnnngh','hp:',self.health,'charge amt', self.chargeAMT)
        if  (self.anim!='chargeup'):
            self.model.play('chargeup')

        if self.chargeAMT >0:
            self.health +=.01
            self.chargeAMT -=.01
        else:
            print('finish charging')
            self.currentBehavior = None
            self.randomizebehavior
        pass
    def processRun(self):
        self.d2p = (self.NP.getPos(render) - self.moveTarget).length()
        if self.inRange == True:
            self.currentBehavior = None
            return
        if self.d2p>2:
            self.run()
        else:
            self.currentBehavior=None
            # self.controller.setLinearMovement(0, False)
            self.speed = 0
    def run(self):#,  target):
     
        target = self.moveTarget
        # if self.d2p < 2:
        #     x=0
          
        dir = self.NP.getQuat().getForward() * 3
     

   
        # self.d2p = (self.NP.getPos(render) - target).length()
      
        # if self.d2p > 2:
        self.NP.lookAt(target)
        self.speed = dir
          
        # self.controller.setLinearMovement(x, False)

        if  (self.anim!='run'):
            self.model.loop('run')

    def idle(self):
        self.speed=0
        def end():
            self.currentBehavior=None
            print('end idle')
        # print('idle')
        if  (self.anim!='idle'):
            self.model.loop('idle')
        if self.frame == 30:
            self.currentBehavior=None

        # idle=self.model.actorInterval('idle',startFrame=0, endFrame = 30 )
        # fin = Func(end)
        # if self.seq!=None:
        #     if self.seq.isPlaying():
        #         self.seq.pause()
        #     self.seq=Sequence(idle, fin)
        #     self.seq.start()

    def chargeHP(self):
        """when enemies spawn in, they charge up their hp. they each have a different starting threshold before theyh become active"""
        print('charging up')
        # chargeseq = Sequence()
        pass
    def isStunned(Self):
        # print('stuned!')
        return