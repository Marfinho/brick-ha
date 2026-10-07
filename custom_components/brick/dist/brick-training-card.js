var kt=Object.defineProperty;var Ct=(n,t,e)=>t in n?kt(n,t,{enumerable:!0,configurable:!0,writable:!0,value:e}):n[t]=e;var b=(n,t,e)=>Ct(n,typeof t!="symbol"?t+"":t,e);var D=globalThis,L=D.ShadowRoot&&(D.ShadyCSS===void 0||D.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,V=Symbol(),at=new WeakMap,C=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==V)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(L&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=at.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&at.set(e,t))}return t}toString(){return this.cssText}},ct=n=>new C(typeof n=="string"?n:n+"",void 0,V),q=(n,...t)=>{let e=n.length===1?n[0]:t.reduce((s,i,o)=>s+(r=>{if(r._$cssResult$===!0)return r.cssText;if(typeof r=="number")return r;throw Error("Value passed to 'css' function must be a 'css' function result: "+r+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+n[o+1],n[0]);return new C(e,n,V)},lt=(n,t)=>{if(L)n.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),i=D.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=e.cssText,n.appendChild(s)}},K=L?n=>n:n=>n instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return ct(e)})(n):n;var{is:Tt,defineProperty:Pt,getOwnPropertyDescriptor:Ht,getOwnPropertyNames:Rt,getOwnPropertySymbols:Ot,getPrototypeOf:Nt}=Object,B=globalThis,ht=B.trustedTypes,Mt=ht?ht.emptyScript:"",Ut=B.reactiveElementPolyfillSupport,T=(n,t)=>n,F={toAttribute(n,t){switch(t){case Boolean:n=n?Mt:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,t){let e=n;switch(t){case Boolean:e=n!==null;break;case Number:e=n===null?null:Number(n);break;case Object:case Array:try{e=JSON.parse(n)}catch{e=null}}return e}},pt=(n,t)=>!Tt(n,t),dt={attribute:!0,type:String,converter:F,reflect:!1,useDefault:!1,hasChanged:pt};Symbol.metadata??=Symbol("metadata"),B.litPropertyMetadata??=new WeakMap;var f=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=dt){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(t,s,e);i!==void 0&&Pt(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){let{get:i,set:o}=Ht(this.prototype,t)??{get(){return this[e]},set(r){this[e]=r}};return{get:i,set(r){let d=i?.call(this);o?.call(this,r),this.requestUpdate(t,d,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??dt}static _$Ei(){if(this.hasOwnProperty(T("elementProperties")))return;let t=Nt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(T("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(T("properties"))){let e=this.properties,s=[...Rt(e),...Ot(e)];for(let i of s)this.createProperty(i,e[i])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,i]of e)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let i=this._$Eu(e,s);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let i of s)e.unshift(K(i))}else t!==void 0&&e.push(K(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return lt(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(i!==void 0&&s.reflect===!0){let o=(s.converter?.toAttribute!==void 0?s.converter:F).toAttribute(e,s.type);this._$Em=t,o==null?this.removeAttribute(i):this.setAttribute(i,o),this._$Em=null}}_$AK(t,e){let s=this.constructor,i=s._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let o=s.getPropertyOptions(i),r=typeof o.converter=="function"?{fromAttribute:o.converter}:o.converter?.fromAttribute!==void 0?o.converter:F;this._$Em=i;let d=r.fromAttribute(e,o.type);this[i]=d??this._$Ej?.get(i)??d,this._$Em=null}}requestUpdate(t,e,s,i=!1,o){if(t!==void 0){let r=this.constructor;if(i===!1&&(o=this[t]),s??=r.getPropertyOptions(t),!((s.hasChanged??pt)(o,e)||s.useDefault&&s.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(r._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:i,wrapped:o},r){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??e??this[t]),o!==!0||r!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),i===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,o]of this._$Ep)this[i]=o;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,o]of s){let{wrapped:r}=o,d=this[i];r!==!0||this._$AL.has(i)||d===void 0||this.C(i,void 0,o,d)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};f.elementStyles=[],f.shadowRootOptions={mode:"open"},f[T("elementProperties")]=new Map,f[T("finalized")]=new Map,Ut?.({ReactiveElement:f}),(B.reactiveElementVersions??=[]).push("2.1.2");var tt=globalThis,ut=n=>n,I=tt.trustedTypes,_t=I?I.createPolicy("lit-html",{createHTML:n=>n}):void 0,bt="$lit$",y=`lit$${Math.random().toFixed(9).slice(2)}$`,vt="?"+y,Dt=`<${vt}>`,w=document,H=()=>w.createComment(""),R=n=>n===null||typeof n!="object"&&typeof n!="function",et=Array.isArray,Lt=n=>et(n)||typeof n?.[Symbol.iterator]=="function",G=`[ 	
\f\r]`,P=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,mt=/-->/g,ft=/>/g,v=RegExp(`>|${G}(?:([^\\s"'>=/]+)(${G}*=${G}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),gt=/'/g,yt=/"/g,At=/^(?:script|style|textarea|title)$/i,st=n=>(t,...e)=>({_$litType$:n,strings:t,values:e}),u=st(1),Zt=st(2),Qt=st(3),S=Symbol.for("lit-noChange"),h=Symbol.for("lit-nothing"),$t=new WeakMap,A=w.createTreeWalker(w,129);function wt(n,t){if(!et(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return _t!==void 0?_t.createHTML(t):t}var Bt=(n,t)=>{let e=n.length-1,s=[],i,o=t===2?"<svg>":t===3?"<math>":"",r=P;for(let d=0;d<e;d++){let a=n[d],c,p,l=-1,_=0;for(;_<a.length&&(r.lastIndex=_,p=r.exec(a),p!==null);)_=r.lastIndex,r===P?p[1]==="!--"?r=mt:p[1]!==void 0?r=ft:p[2]!==void 0?(At.test(p[2])&&(i=RegExp("</"+p[2],"g")),r=v):p[3]!==void 0&&(r=v):r===v?p[0]===">"?(r=i??P,l=-1):p[1]===void 0?l=-2:(l=r.lastIndex-p[2].length,c=p[1],r=p[3]===void 0?v:p[3]==='"'?yt:gt):r===yt||r===gt?r=v:r===mt||r===ft?r=P:(r=v,i=void 0);let g=r===v&&n[d+1].startsWith("/>")?" ":"";o+=r===P?a+Dt:l>=0?(s.push(c),a.slice(0,l)+bt+a.slice(l)+y+g):a+y+(l===-2?d:g)}return[wt(n,o+(n[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},O=class n{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let o=0,r=0,d=t.length-1,a=this.parts,[c,p]=Bt(t,e);if(this.el=n.createElement(c,s),A.currentNode=this.el.content,e===2||e===3){let l=this.el.content.firstChild;l.replaceWith(...l.childNodes)}for(;(i=A.nextNode())!==null&&a.length<d;){if(i.nodeType===1){if(i.hasAttributes())for(let l of i.getAttributeNames())if(l.endsWith(bt)){let _=p[r++],g=i.getAttribute(l).split(y),U=/([.?@])?(.*)/.exec(_);a.push({type:1,index:o,name:U[2],strings:g,ctor:U[1]==="."?Y:U[1]==="?"?Z:U[1]==="@"?Q:x}),i.removeAttribute(l)}else l.startsWith(y)&&(a.push({type:6,index:o}),i.removeAttribute(l));if(At.test(i.tagName)){let l=i.textContent.split(y),_=l.length-1;if(_>0){i.textContent=I?I.emptyScript:"";for(let g=0;g<_;g++)i.append(l[g],H()),A.nextNode(),a.push({type:2,index:++o});i.append(l[_],H())}}}else if(i.nodeType===8)if(i.data===vt)a.push({type:2,index:o});else{let l=-1;for(;(l=i.data.indexOf(y,l+1))!==-1;)a.push({type:7,index:o}),l+=y.length-1}o++}}static createElement(t,e){let s=w.createElement("template");return s.innerHTML=t,s}};function E(n,t,e=n,s){if(t===S)return t;let i=s!==void 0?e._$Co?.[s]:e._$Cl,o=R(t)?void 0:t._$litDirective$;return i?.constructor!==o&&(i?._$AO?.(!1),o===void 0?i=void 0:(i=new o(n),i._$AT(n,e,s)),s!==void 0?(e._$Co??=[])[s]=i:e._$Cl=i),i!==void 0&&(t=E(n,i._$AS(n,t.values),i,s)),t}var J=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??w).importNode(e,!0);A.currentNode=i;let o=A.nextNode(),r=0,d=0,a=s[0];for(;a!==void 0;){if(r===a.index){let c;a.type===2?c=new N(o,o.nextSibling,this,t):a.type===1?c=new a.ctor(o,a.name,a.strings,this,t):a.type===6&&(c=new X(o,this,t)),this._$AV.push(c),a=s[++d]}r!==a?.index&&(o=A.nextNode(),r++)}return A.currentNode=w,i}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},N=class n{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=h,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=E(this,t,e),R(t)?t===h||t==null||t===""?(this._$AH!==h&&this._$AR(),this._$AH=h):t!==this._$AH&&t!==S&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Lt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==h&&R(this._$AH)?this._$AA.nextSibling.data=t:this.T(w.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,i=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=O.createElement(wt(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{let o=new J(i,this),r=o.u(this.options);o.p(e),this.T(r),this._$AH=o}}_$AC(t){let e=$t.get(t.strings);return e===void 0&&$t.set(t.strings,e=new O(t)),e}k(t){et(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,i=0;for(let o of t)i===e.length?e.push(s=new n(this.O(H()),this.O(H()),this,this.options)):s=e[i],s._$AI(o),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=ut(t).nextSibling;ut(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},x=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,o){this.type=1,this._$AH=h,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=o,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=h}_$AI(t,e=this,s,i){let o=this.strings,r=!1;if(o===void 0)t=E(this,t,e,0),r=!R(t)||t!==this._$AH&&t!==S,r&&(this._$AH=t);else{let d=t,a,c;for(t=o[0],a=0;a<o.length-1;a++)c=E(this,d[s+a],e,a),c===S&&(c=this._$AH[a]),r||=!R(c)||c!==this._$AH[a],c===h?t=h:t!==h&&(t+=(c??"")+o[a+1]),this._$AH[a]=c}r&&!i&&this.j(t)}j(t){t===h?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},Y=class extends x{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===h?void 0:t}},Z=class extends x{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==h)}},Q=class extends x{constructor(t,e,s,i,o){super(t,e,s,i,o),this.type=5}_$AI(t,e=this){if((t=E(this,t,e,0)??h)===S)return;let s=this._$AH,i=t===h&&s!==h||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,o=t!==h&&(s===h||i);i&&this.element.removeEventListener(this.name,this,s),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},X=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){E(this,t)}};var It=tt.litHtmlPolyfillSupport;It?.(O,N),(tt.litHtmlVersions??=[]).push("3.3.3");var St=(n,t,e)=>{let s=e?.renderBefore??t,i=s._$litPart$;if(i===void 0){let o=e?.renderBefore??null;s._$litPart$=i=new N(t.insertBefore(H(),o),o,void 0,e??{})}return i._$AI(n),i};var it=globalThis,m=class extends f{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=St(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return S}};m._$litElement$=!0,m.finalized=!0,it.litElementHydrateSupport?.({LitElement:m});var zt=it.litElementPolyfillSupport;zt?.({LitElement:m});(it.litElementVersions??=[]).push("4.2.2");var jt={de:{title:"Brick Training",open_one:"1 Einheit offen",open_many:"{n} Einheiten offen",all_done:"Alles erledigt",nothing:"Heute ist nichts geplant",status_open:"offen",status_done:"erledigt",announce:"Ansagen",announced:"Ansage gestartet",announce_failed:"Ansage fehlgeschlagen",unavailable:"Brick ist gerade nicht verfügbar.",not_found:"Entität {entity} nicht gefunden.",week:"Nächste 7 Tage",hour_min:"{h} Std {m}",hours:"{h} Std",minutes:"{m} Min",editor_entity:"Entität „Training heute“",editor_week_entity:"Entität „Training Woche“ (optional)",editor_title:"Titel",editor_show_done:"Erledigte Einheiten anzeigen",editor_show_announce:"Knopf „Ansagen“ anzeigen",editor_media_player:"Lautsprecher für die Ansage",editor_tts_entity:"TTS-Dienst für die Ansage"},en:{title:"Brick Training",open_one:"1 session open",open_many:"{n} sessions open",all_done:"All done",nothing:"Nothing planned today",status_open:"open",status_done:"done",announce:"Announce",announced:"Announcement started",announce_failed:"Announcement failed",unavailable:"Brick is currently unavailable.",not_found:"Entity {entity} not found.",week:"Next 7 days",hour_min:"{h} h {m}",hours:"{h} h",minutes:"{m} min",editor_entity:'"Training today" entity',editor_week_entity:'"Training week" entity (optional)',editor_title:"Title",editor_show_done:"Show completed sessions",editor_show_announce:'Show "Announce" button',editor_media_player:"Speaker for the announcement",editor_tts_entity:"TTS service for the announcement"}};function z(n){return(n?.locale?.language??n?.language??"en").toLowerCase().startsWith("de")?"de":"en"}function $(n,t,e={}){let s=jt[z(n)][t];for(let[i,o]of Object.entries(e))s=s.replaceAll(`{${i}}`,String(o));return s}var Wt={run:"mdi:run",bike:"mdi:bike",swim:"mdi:swim",strength:"mdi:dumbbell",mobility:"mdi:yoga",walk:"mdi:walk",brick:"mdi:weight-lifter",cross_training:"mdi:weight-lifter",rest:"mdi:sleep"};function nt(n){return Wt[n]??"mdi:heart-pulse"}function Et(n,t){if(!Number.isFinite(t)||t<=0)return"";let e=Math.floor(t/60),s=Math.round(t%60);return e===0?$(n,"minutes",{m:s}):s===0?$(n,"hours",{h:e}):$(n,"hour_min",{h:e,m:s})}function ot(n){let t=/^(\d{4})-(\d{2})-(\d{2})$/.exec(n);if(t)return new Date(Number(t[1]),Number(t[2])-1,Number(t[3]),12)}function j(n){let t=e=>String(e).padStart(2,"0");return`${n.getFullYear()}-${t(n.getMonth()+1)}-${t(n.getDate())}`}function rt(n){return Array.isArray(n)?n.filter(t=>typeof t=="object"&&t!==null&&"sport"in t):[]}var xt=new Set(["unavailable","unknown"]),k=class extends m{constructor(){super(...arguments);b(this,"_announce",async()=>{let e=this._config?.announce;if(!(!e?.media_player||!this.hass)){try{await this.hass.callService("brick","announce",{day:"today",media_player:[e.media_player],...e.tts_entity?{tts_entity:e.tts_entity}:{}}),this._feedback=this._t("announced")}catch{this._feedback=this._t("announce_failed")}window.setTimeout(()=>{this._feedback=void 0},4e3)}})}static getConfigElement(){return document.createElement("brick-training-card-editor")}static getStubConfig(e){let s=Object.keys(e?.states??{}).find(o=>o.startsWith("sensor.brick_training_heute"))??"sensor.brick_training_heute",i=Object.keys(e?.states??{}).find(o=>o.startsWith("sensor.brick_training_woche"));return{entity:s,...i?{week_entity:i}:{}}}setConfig(e){if(!e||typeof e.entity!="string"||!e.entity)throw new Error("entity is required");this._config={show_done:!0,show_announce_button:!0,...e}}getCardSize(){let e=this._items(this._stateObj()).length;return 2+Math.min(e,6)+(this._config?.week_entity?2:0)}getGridOptions(){return{columns:12,min_columns:6,min_rows:3}}_stateObj(){return this._config?this.hass?.states[this._config.entity]:void 0}_items(e){return rt(e?.attributes.items)}_t(e,s){return $(this.hass,e,s)}render(){if(!this._config||!this.hass)return h;let e=this._config,s=e.title??this._t("title"),i=this._stateObj();if(!i)return this._shell(s,u`<p class="message" role="alert">${this._t("not_found",{entity:e.entity})}</p>`);if(xt.has(i.state))return this._shell(s,u`<p class="message" role="status">${this._t("unavailable")}</p>`);let o=this._items(i),r=e.show_done===!1?o.filter(p=>p.status!=="done"):o,d=Number.parseInt(i.state,10)||0,a=Number(i.attributes.done_count??0),c=this._summary(d,a);return this._shell(s,u`
        <div class="head">
          <div>
            <div class="date">${this._dateLabel(i)}</div>
            <div class="state" role="status">${c}</div>
          </div>
          ${this._announceButton()}
        </div>
        ${r.length?u`<ul class="items" aria-label=${s}>
              ${r.map(p=>this._item(p))}
            </ul>`:h}
        ${this._feedback?u`<p class="feedback" role="status">${this._feedback}</p>`:h}
        ${this._week()}
      `)}_shell(e,s){return u`<ha-card .header=${e}><div class="content">${s}</div></ha-card>`}_summary(e,s){return e>0?e===1?this._t("open_one"):this._t("open_many",{n:e}):s>0?this._t("all_done"):this._t("nothing")}_dateLabel(e){let s=String(e.attributes.date??""),i=ot(s);return i?i.toLocaleDateString(z(this.hass),{weekday:"long",day:"numeric",month:"long"}):""}_item(e){let s=e.status==="done",i=Et(this.hass,e.durationMin);return u`
      <li class="item ${s?"done":""}">
        <ha-icon class="sport" .icon=${nt(e.sport)} aria-hidden="true"></ha-icon>
        <span class="title">${e.title}</span>
        ${i?u`<span class="duration">${i}</span>`:h}
        <span class="chip ${s?"chip-done":"chip-open"}">
          ${s?this._t("status_done"):this._t("status_open")}
        </span>
      </li>
    `}_week(){let e=this._config?.week_entity;if(!e)return h;let s=this.hass?.states[e];if(!s||xt.has(s.state))return h;let i=new Map;for(let c of rt(s.attributes.items))i.set(c.date,[...i.get(c.date)??[],c]);let o=String(this._stateObj()?.attributes.date??"")||j(new Date),r=ot(o)??new Date,d=z(this.hass),a=Array.from({length:7},(c,p)=>{let l=new Date(r.getFullYear(),r.getMonth(),r.getDate()+p,12);return{date:l,iso:j(l),items:i.get(j(l))??[]}});return u`
      <ol class="week" aria-label=${this._t("week")}>
        ${a.map(c=>{let p=c.date.toLocaleDateString(d,{weekday:"long",day:"numeric",month:"long"}),l=c.iso===o;return u`
            <li class="day ${l?"today":""}" aria-label=${p} aria-current=${l?"date":h}>
              <span class="dow">${c.date.toLocaleDateString(d,{weekday:"short"})}</span>
              <span class="dom">${c.date.getDate()}</span>
              <span class="dots">
                ${c.items.map(_=>u`<ha-icon
                    class="dot ${_.status==="done"?"dot-done":""}"
                    .icon=${nt(_.sport)}
                    title=${_.title}
                  ></ha-icon>`)}
              </span>
            </li>
          `})}
      </ol>
    `}_announceButton(){let e=this._config;return!e||e.show_announce_button===!1?h:e.announce?.media_player?u`<button class="announce" type="button" @click=${this._announce}>
      <ha-icon icon="mdi:bullhorn" aria-hidden="true"></ha-icon>
      <span>${this._t("announce")}</span>
    </button>`:h}};b(k,"properties",{hass:{attribute:!1},_config:{state:!0},_feedback:{state:!0}}),b(k,"styles",q`
    .content {
      padding: 0 16px 16px;
      color: var(--primary-text-color);
    }
    .head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
    }
    .date {
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s, 0.875rem);
    }
    .state {
      font-size: var(--ha-font-size-xl, 1.25rem);
      font-weight: 500;
    }
    .message {
      margin: 0;
      color: var(--secondary-text-color);
    }
    .items,
    .week {
      list-style: none;
      margin: 0;
      padding: 0;
    }
    .item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 0;
      border-top: 1px solid var(--divider-color);
    }
    .sport {
      color: var(--primary-color);
      flex: none;
    }
    .title {
      flex: 1;
      min-width: 0;
      overflow-wrap: anywhere;
    }
    .duration {
      color: var(--secondary-text-color);
      white-space: nowrap;
    }
    .chip {
      flex: none;
      padding: 2px 10px;
      border-radius: 12px;
      font-size: var(--ha-font-size-s, 0.8125rem);
      border: 1px solid var(--primary-color);
      color: var(--primary-text-color);
    }
    .chip-done {
      border-color: var(--divider-color);
      color: var(--secondary-text-color);
    }
    .item.done .title,
    .item.done .duration {
      text-decoration: line-through;
    }
    .item.done {
      opacity: 0.65;
    }
    .announce {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      flex: none;
      padding: 8px 14px;
      border: 0;
      border-radius: 18px;
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
      font: inherit;
      cursor: pointer;
    }
    .announce:focus-visible,
    .announce:hover {
      outline: 2px solid var(--primary-text-color);
      outline-offset: 2px;
    }
    .feedback {
      margin: 8px 0 0;
      color: var(--secondary-text-color);
    }
    .week {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 4px;
      margin-top: 12px;
    }
    .day {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      padding: 6px 2px;
      border-radius: 8px;
      border: 1px solid var(--divider-color);
      min-width: 0;
    }
    .day.today {
      border-color: var(--primary-color);
      background: var(--secondary-background-color);
      font-weight: 600;
    }
    .dow {
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s, 0.75rem);
    }
    .dots {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      min-height: 16px;
    }
    .dot {
      --mdc-icon-size: 16px;
      color: var(--primary-color);
    }
    .dot-done {
      color: var(--secondary-text-color);
      opacity: 0.6;
    }
  `);var Vt=[{name:"entity",required:!0,selector:{entity:{domain:"sensor",integration:"brick"}}},{name:"week_entity",selector:{entity:{domain:"sensor",integration:"brick"}}},{name:"title",selector:{text:{}}},{name:"show_done",selector:{boolean:{}}},{name:"show_announce_button",selector:{boolean:{}}},{name:"media_player",selector:{entity:{domain:"media_player"}}},{name:"tts_entity",selector:{entity:{domain:"tts"}}}],qt={entity:"editor_entity",week_entity:"editor_week_entity",title:"editor_title",show_done:"editor_show_done",show_announce_button:"editor_show_announce",media_player:"editor_media_player",tts_entity:"editor_tts_entity"},M=class extends m{constructor(){super(...arguments);b(this,"_changed",e=>{e.stopPropagation();let s=e.detail.value,i={type:this._config?.type??"custom:brick-training-card",entity:s.entity??""};s.week_entity&&(i.week_entity=s.week_entity),s.title&&(i.title=s.title),i.show_done=s.show_done??!0,i.show_announce_button=s.show_announce_button??!0,(s.media_player||s.tts_entity)&&(i.announce={...s.media_player?{media_player:s.media_player}:{},...s.tts_entity?{tts_entity:s.tts_entity}:{}}),this._config=i,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:i},bubbles:!0,composed:!0}))})}setConfig(e){this._config=e}render(){if(!this._config)return h;let e=this._config,s={entity:e.entity,week_entity:e.week_entity,title:e.title,show_done:e.show_done??!0,show_announce_button:e.show_announce_button??!0,media_player:e.announce?.media_player,tts_entity:e.announce?.tts_entity};return u`<ha-form
      .hass=${this.hass}
      .data=${s}
      .schema=${Vt}
      .computeLabel=${i=>$(this.hass,qt[i.name]??"title")}
      @value-changed=${this._changed}
    ></ha-form>`}};b(M,"properties",{hass:{attribute:!1},_config:{state:!0}});customElements.get("brick-training-card")||customElements.define("brick-training-card",k);customElements.get("brick-training-card-editor")||customElements.define("brick-training-card-editor",M);var W=window;W.customCards=W.customCards??[];W.customCards.some(n=>n.type==="brick-training-card")||W.customCards.push({type:"brick-training-card",name:"Brick Training",description:"Heutiges Training und 7-Tage-Übersicht aus Brick / Today's training and 7-day overview from Brick",preview:!1,documentationURL:"https://github.com/Marfinho/brick-ha"});
