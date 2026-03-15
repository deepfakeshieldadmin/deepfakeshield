/* ═══════════════════════════════════════════════════════════════
   DeepFake Shield — Preferences
   ═══════════════════════════════════════════════════════════════ */
(function(){
    'use strict';
    var KEY = 'dfs_prefs';
    var defaults = {
        fontSize: 'normal',
        reducedMotion: false,
        accent: 'default'
    };

    function load(){
        try {
            var s = localStorage.getItem(KEY);
            return s ? Object.assign({}, defaults, JSON.parse(s)) : Object.assign({}, defaults);
        } catch(e){ return Object.assign({}, defaults); }
    }

    function save(p){
        try { localStorage.setItem(KEY, JSON.stringify(p)); } catch(e){}
    }

    function apply(p){
        var sizes = {small:'14px', normal:'16px', large:'18px'};
        document.documentElement.style.fontSize = sizes[p.fontSize] || '16px';
        if(p.reducedMotion){
            document.documentElement.classList.add('reduced-motion');
        } else {
            document.documentElement.classList.remove('reduced-motion');
        }
        save(p);
    }

    document.addEventListener('DOMContentLoaded', function(){
        apply(load());
        if(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches){
            var p = load(); p.reducedMotion = true; apply(p);
        }
    });

    window.DFSPrefs = {
        load: load, save: save, apply: apply,
        set: function(k,v){ var p=load(); p[k]=v; apply(p); },
        get: function(k){ return load()[k]; }
    };
})();