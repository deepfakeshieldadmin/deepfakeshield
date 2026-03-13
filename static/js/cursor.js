/* ═══════════════════════════════════════════════════════════
   DEEP FAKE SHIELD — CURSOR EFFECTS v3
   Standard pointer stays. Animated effects trail behind.
   ═══════════════════════════════════════════════════════════ */
(function(){
    let canvas,ctx,particles=[],mx=-100,my=-100,pmx=-100,pmy=-100;
    let curStyle=localStorage.getItem('dfs-cursor')||'default';
    let running=false;

    function isDark(){return document.documentElement.getAttribute('data-theme')==='dark';}

    function init(){
        canvas=document.createElement('canvas');
        canvas.id='cursorFxCanvas';
        canvas.style.cssText='position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:999999;pointer-events:none;';
        document.body.appendChild(canvas);
        ctx=canvas.getContext('2d');
        resize();
        window.addEventListener('resize',resize);
        document.addEventListener('mousemove',onMove);
        document.addEventListener('mousedown',onClick);
        applyCursor(curStyle);
    }

    function resize(){canvas.width=innerWidth;canvas.height=innerHeight;}

    function onMove(e){
        pmx=mx;pmy=my;mx=e.clientX;my=e.clientY;
        const speed=Math.sqrt((mx-pmx)**2+(my-pmy)**2);
        if(curStyle!=='default'&&speed>1)spawnParticles(speed);
    }

    function onClick(){
        if(curStyle==='default')return;
        for(let i=0;i<25;i++)spawnParticles(30);
    }

    function spawnParticles(speed){
        const n=Math.min(Math.floor(speed/3)+1,8);
        const dark=isDark();
        switch(curStyle){
            case'shadow-fire':shadowFire(n,dark);break;
            case'katana':katanaSlash(n,dark);break;
            case'binary':binaryRain(n,dark);break;
            case'circuit':circuitPulse(n,dark);break;
            case'pixel':pixelTrail(n,dark);break;
            case'lightning':lightningBolt(n,dark);break;
        }
        if(!running)startAnim();
    }

    // ═══ SHADOW FIRE — Purple/dark flames ═══
    function shadowFire(n,dark){
        for(let i=0;i<n;i++){
            // Purple-dark shadow flames (like Solo Leveling)
            const colors=dark
                ?[{r:120,g:0,b:255},{r:80,g:0,b:200},{r:150,g:50,b:255},{r:60,g:0,b:180},{r:100,g:20,b:220}]
                :[{r:255,g:120,b:0},{r:255,g:80,b:0},{r:255,g:180,b:30},{r:200,g:50,b:0},{r:255,g:150,b:50}];
            const c=colors[Math.floor(Math.random()*colors.length)];
            particles.push({
                x:mx+(Math.random()-0.5)*12,y:my+(Math.random()-0.5)*12,
                vx:(Math.random()-0.5)*2,vy:-(Math.random()*4+2),
                life:1,decay:Math.random()*0.02+0.01,
                size:Math.random()*8+4,r:c.r,g:c.g,b:c.b,type:'sfire',
                sway:(Math.random()-0.5)*0.3,shrink:0.96
            });
        }
        // Hot embers
        if(Math.random()>0.4){
            particles.push({
                x:mx+(Math.random()-0.5)*15,y:my,
                vx:(Math.random()-0.5)*4,vy:-(Math.random()*5+3),
                life:1,decay:0.018,size:Math.random()*2.5+1,
                r:255,g:dark?200:255,b:dark?255:150,type:'ember'
            });
        }
    }

    // ═══ KATANA SLASH — Blade shape ═══
    function katanaSlash(n,dark){
        const angle=Math.atan2(my-pmy,mx-pmx);
        // Main slash
        if(Math.random()>0.2){
            particles.push({
                x:mx,y:my,angle:angle,
                len:Math.random()*45+25,
                life:1,decay:0.045,
                type:'katana',
                r:dark?180:220,g:dark?200:230,b:255,
                width:Math.random()*3+2,
                curve:(Math.random()-0.5)*0.3
            });
        }
        // Metal sparks
        for(let i=0;i<Math.min(n,4);i++){
            const a=angle+(Math.random()-0.5)*1.5;
            particles.push({
                x:mx,y:my,
                vx:Math.cos(a)*(Math.random()*5+3),vy:Math.sin(a)*(Math.random()*5+3),
                life:1,decay:0.035,size:Math.random()*1.5+0.5,
                r:220,g:230,b:255,type:'spark'
            });
        }
    }

    // ═══ BINARY RAIN ═══
    function binaryRain(n,dark){
        if(Math.random()>0.3){
            const ch=['0','1','{','}','<','>','/','#','$','@','int','if','for','var','fn'];
            particles.push({
                x:mx+(Math.random()-0.5)*35,y:my,
                vx:0,vy:Math.random()*2.5+1,
                life:1,decay:Math.random()*0.01+0.005,
                char:ch[Math.floor(Math.random()*ch.length)],
                size:Math.random()*8+10,
                r:0,g:dark?255:180,b:dark?100:0,type:'binary'
            });
        }
    }

    // ═══ CIRCUIT PULSE ═══
    function circuitPulse(n,dark){
        if(Math.random()>0.4){
            const dir=Math.floor(Math.random()*8);
            const angles=[0,Math.PI/4,Math.PI/2,3*Math.PI/4,Math.PI,5*Math.PI/4,3*Math.PI/2,7*Math.PI/4];
            const a=angles[dir];
            particles.push({
                x:mx,y:my,
                dx:Math.cos(a),dy:Math.sin(a),
                speed:Math.random()*4+2,dist:0,
                maxDist:Math.random()*50+25,
                life:1,decay:0.018,
                r:0,g:dark?220:160,b:255,type:'circuit',w:2
            });
        }
        if(Math.random()>0.6){
            particles.push({
                x:mx+(Math.random()-0.5)*20,y:my+(Math.random()-0.5)*20,
                life:1,decay:0.03,size:Math.random()*4+2,
                r:0,g:dark?255:200,b:255,type:'node'
            });
        }
    }

    // ═══ PIXEL TRAIL ═══
    function pixelTrail(n,dark){
        for(let i=0;i<Math.min(n,5);i++){
            const cs=[{r:255,g:50,b:50},{r:50,g:255,b:50},{r:50,g:100,b:255},{r:255,g:255,b:50},{r:255,g:50,b:255},{r:50,g:255,b:255}];
            const c=cs[Math.floor(Math.random()*cs.length)];
            particles.push({
                x:mx+(Math.random()-0.5)*12,y:my+(Math.random()-0.5)*12,
                vx:(Math.random()-0.5)*2.5,vy:(Math.random()-0.5)*2.5+0.5,
                life:1,decay:Math.random()*0.02+0.008,
                size:Math.random()*5+3,r:c.r,g:c.g,b:c.b,type:'pixel'
            });
        }
    }

    // ═══ LIGHTNING ═══
    function lightningBolt(n,dark){
        if(Math.random()>0.4){
            const pts=[{x:mx,y:my}];
            let cx=mx,cy=my;
            for(let i=0;i<Math.floor(Math.random()*5)+3;i++){
                cx+=(Math.random()-0.5)*35;
                cy+=Math.random()*18+5;
                pts.push({x:cx,y:cy});
            }
            particles.push({
                points:pts,life:1,decay:0.055,
                r:dark?150:100,g:dark?200:180,b:255,
                type:'lightning',w:Math.random()*2.5+1
            });
        }
    }

    // ═══ ANIMATION ═══
    function startAnim(){running=true;animate();}

    function animate(){
        if(particles.length===0){running=false;ctx.clearRect(0,0,canvas.width,canvas.height);return;}
        ctx.clearRect(0,0,canvas.width,canvas.height);

        for(let i=particles.length-1;i>=0;i--){
            const p=particles[i];
            p.life-=p.decay;
            if(p.life<=0){particles.splice(i,1);continue;}
            switch(p.type){
                case'sfire':drawShadowFire(p);break;
                case'ember':drawEmber(p);break;
                case'katana':drawKatana(p);break;
                case'spark':drawSpark(p);break;
                case'binary':drawBinary(p);break;
                case'circuit':drawCircuit(p);break;
                case'node':drawNode(p);break;
                case'pixel':drawPixel(p);break;
                case'lightning':drawLightning(p);break;
            }
        }
        if(particles.length>350)particles.splice(0,particles.length-350);
        requestAnimationFrame(animate);
    }

    // ═══ DRAW FUNCTIONS ═══

    function drawShadowFire(p){
        p.vx+=p.sway;p.vy-=0.06;p.x+=p.vx;p.y+=p.vy;p.size*=p.shrink;
        const a=p.life*(0.8+Math.sin(Date.now()*0.01+p.x)*0.2);
        ctx.save();
        // Outer glow
        const g=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.size*2.5);
        g.addColorStop(0,`rgba(${p.r},${p.g},${p.b},${a*0.7})`);
        g.addColorStop(0.5,`rgba(${p.r},${p.g},${p.b},${a*0.3})`);
        g.addColorStop(1,`rgba(${p.r},${p.g},${p.b},0)`);
        ctx.fillStyle=g;ctx.beginPath();ctx.arc(p.x,p.y,p.size*2.5,0,Math.PI*2);ctx.fill();
        // Bright core
        const g2=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.size*0.6);
        g2.addColorStop(0,`rgba(255,255,255,${a*0.5})`);
        g2.addColorStop(1,`rgba(${p.r},${p.g},${p.b},${a*0.3})`);
        ctx.fillStyle=g2;ctx.beginPath();ctx.arc(p.x,p.y,p.size*0.6,0,Math.PI*2);ctx.fill();
        ctx.restore();
    }

    function drawEmber(p){
        p.vy-=0.04;p.x+=p.vx;p.y+=p.vy;p.vx*=0.97;
        ctx.save();ctx.fillStyle=`rgba(${p.r},${p.g},${p.b},${p.life})`;
        ctx.shadowColor=`rgba(${p.r},${p.g},${p.b},${p.life})`;ctx.shadowBlur=8;
        ctx.beginPath();ctx.arc(p.x,p.y,p.size,0,Math.PI*2);ctx.fill();ctx.restore();
    }

    function drawKatana(p){
        ctx.save();
        const ex=p.x+Math.cos(p.angle)*p.len*p.life;
        const ey=p.y+Math.sin(p.angle)*p.len*p.life;
        // Blade body — tapered line
        const perpAngle=p.angle+Math.PI/2;
        const w=p.width*p.life;
        ctx.beginPath();
        ctx.moveTo(p.x,p.y);
        // Curved blade
        const cpx=p.x+Math.cos(p.angle)*p.len*0.5+Math.cos(perpAngle+p.curve)*w*3;
        const cpy=p.y+Math.sin(p.angle)*p.len*0.5+Math.sin(perpAngle+p.curve)*w*3;
        ctx.quadraticCurveTo(cpx,cpy,ex,ey);
        ctx.strokeStyle=`rgba(${p.r},${p.g},${p.b},${p.life*0.9})`;
        ctx.lineWidth=w;ctx.lineCap='round';
        ctx.shadowColor=`rgba(${p.r},${p.g},${p.b},${p.life*0.6})`;ctx.shadowBlur=20;
        ctx.stroke();
        // White edge
        ctx.strokeStyle=`rgba(255,255,255,${p.life*0.4})`;
        ctx.lineWidth=w*0.3;ctx.stroke();
        ctx.restore();
    }

    function drawSpark(p){
        p.x+=p.vx;p.y+=p.vy;p.vy+=0.12;p.vx*=0.96;
        ctx.save();ctx.fillStyle=`rgba(${p.r},${p.g},${p.b},${p.life})`;
        ctx.shadowColor=`rgba(${p.r},${p.g},${p.b},${p.life})`;ctx.shadowBlur=5;
        ctx.beginPath();ctx.arc(p.x,p.y,p.size,0,Math.PI*2);ctx.fill();ctx.restore();
    }

    function drawBinary(p){
        p.x+=p.vx;p.y+=p.vy;
        ctx.save();ctx.font=p.size+'px "Share Tech Mono",monospace';
        ctx.fillStyle=`rgba(${p.r},${p.g},${p.b},${p.life})`;
        ctx.shadowColor=`rgba(${p.r},${p.g},${p.b},${p.life*0.5})`;ctx.shadowBlur=10;
        ctx.fillText(p.char,p.x,p.y);ctx.restore();
        if(Math.random()>0.9)p.char=['0','1','<','>','/','{','}'][Math.floor(Math.random()*7)];
    }

    function drawCircuit(p){
        const ex=p.x+p.dx*p.dist,ey=p.y+p.dy*p.dist;
        p.dist+=p.speed;if(p.dist>=p.maxDist)p.life=0;
        ctx.save();ctx.strokeStyle=`rgba(${p.r},${p.g},${p.b},${p.life})`;
        ctx.lineWidth=p.w;ctx.shadowColor=`rgba(${p.r},${p.g},${p.b},${p.life*0.5})`;ctx.shadowBlur=8;
        ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(ex,ey);ctx.stroke();
        ctx.fillStyle=`rgba(${p.r},${p.g},${p.b},${p.life})`;
        ctx.beginPath();ctx.arc(ex,ey,3,0,Math.PI*2);ctx.fill();ctx.restore();
    }

    function drawNode(p){
        ctx.save();ctx.fillStyle=`rgba(${p.r},${p.g},${p.b},${p.life})`;
        ctx.shadowColor=`rgba(${p.r},${p.g},${p.b},${p.life})`;ctx.shadowBlur=12;
        ctx.beginPath();ctx.arc(p.x,p.y,p.size*p.life,0,Math.PI*2);ctx.fill();ctx.restore();
    }

    function drawPixel(p){
        p.x+=p.vx;p.y+=p.vy;
        ctx.save();ctx.fillStyle=`rgba(${p.r},${p.g},${p.b},${p.life})`;
        ctx.fillRect(Math.floor(p.x),Math.floor(p.y),p.size,p.size);ctx.restore();
    }

    function drawLightning(p){
        ctx.save();ctx.strokeStyle=`rgba(${p.r},${p.g},${p.b},${p.life})`;
        ctx.lineWidth=p.w*p.life;ctx.shadowColor=`rgba(${p.r},${p.g},${p.b},${p.life})`;
        ctx.shadowBlur=18;ctx.lineJoin='round';ctx.beginPath();
        ctx.moveTo(p.points[0].x,p.points[0].y);
        for(let i=1;i<p.points.length;i++)ctx.lineTo(p.points[i].x,p.points[i].y);
        ctx.stroke();
        ctx.strokeStyle=`rgba(255,255,255,${p.life*0.3})`;
        ctx.lineWidth=p.w*p.life*2.5;ctx.stroke();ctx.restore();
    }

    // ═══ APPLY CURSOR ═══
    function applyCursor(style){
        curStyle=style;localStorage.setItem('dfs-cursor',style);
        particles=[];
        document.body.style.cursor='auto'; // ALWAYS keep standard pointer
        canvas.style.display=(style==='default')?'none':'block';
    }

    window.setCursorStyle=function(style){
        applyCursor(style);
        if(typeof showToast==='function'){
            const names={'default':'🔹 Default','shadow-fire':'🔥 Shadow Fire','katana':'⚔️ Katana Slash','binary':'💻 Binary Rain','circuit':'🔌 Circuit Pulse','pixel':'🎮 Pixel Trail','lightning':'⚡ Lightning'};
            showToast('Cursor: '+(names[style]||style));
        }
    };

    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);
    else init();
})();