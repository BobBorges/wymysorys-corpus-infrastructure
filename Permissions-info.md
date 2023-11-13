# Permissions info per view

Permissions levels (L-->H)

    - no auth
        - can view
            + landing
            + about
            + document_overview (no forms)
            + document_meta (no forms)
            + markup_reference
            + seaerch
            
        - can't view
            + asset_overview
            + asset_view
            + author_overview
            + author_view
            + admin panel
            + document_content
            + document_markup
            
    - public (authenticated w/ explicit permissions assignment)
        - can view
            + landing
            + about
            + asset_overview (only sees N assets, not list of files)
            + author_overview (no add author form
            + author_view (no access to Forms)
            + document_overview (no access to forms)
            + document_meta (no access to forms)
            + markup_reference 
            + seaerch
            
        - can't view
            + asset_view
            + document_content
            + document_markup
            + admin panel

    - contributor
        - can view
            + landing
            + about
            + asset overview (sees assets where `showonui` == True)
            + asset view (no access to `AssignAssetForm()`)
            + author_overview
            + author_view (can add bio and alt names)
            + document_overview
            + document_meta (can use add forms + edit meta data)
            + document_content
            + markup_reference 
            + seaerch
            
        - can't view
            + document markup
            + admin panel
        
    - worker
        - can view
            + landing
            + about
            + asset overview (sees assets where `showonui` == True)
            + asset view
            + author_overview
            + author_view
            + document_overview
            + document_meta (can use add / edit w/ all forms)
            + document_content
            + document markup
            + markup_reference 
            + seaerch
            
        - can't view 
            + admin panel
    
    - admin
        
        (in theory 'admin' users can do everything, but they must explicitly be given access to the admin panel)
        
        - can view
            + landing
            + about
            + asset overview (sees assets where `showonui` == True)
            + asset view
            + author_overview
            + author_view
            + document_overview
            + document_meta (can use add / edit w/ all forms
            + document_content
            + document markup
            + markup_reference 
            + seaerch
            + admin panel
            
        - can't view
        
        

## `landing`

    no login required
    
    
    
## `about`

    no login required
    
    
    
    
## `asset_overview`

    - Who has access?

        - all (login)
    
    - Who sees what?

        - contributors and workers see Asset objects with `showonui` == True
        - admin sees all Asset Objects
        - public sees only N objects
    
    - View function renders appropriate Asset objects, template handles differences.




## `asset_view`

    - Who has access?
    
        - contributor and above
        - worker and above have access to AssignAssetForm and can assign assets to documents
        
    - Who sees what
    
        - only admin users see hidden assets 
        
    - View functions render appropriate Asset objects or redirect




## `author_overview`

    - Who has access?
    
        -all (login)
        
    - Who sees what??
    
        - contributor and above gets "add author form"




## `author_view`

    - Who has access?
    
        -all (login)
        
    - Who sees what?
    
        - contributor and above get
            -add alt-name form
            -add bio form
            
        - worker and above get edit bio form
        
        
        
        
## `document_overview`

    - Who has access?
    
        - all (no login)
        
    - Who see's what?
    
        - contributor and above has access add-doc form



## `document_meta`

    - Who has access?
    
        - all (no login)
        
    - Who can see what?
    
        - contributor and above have access to 
            - add / edit extended metadata
            - add descriptions
            - get link to browse document_content (if doc-ready)
            
        - worker and above 
            - can edit descriptions
            - get link to markup (if active)




## `document_content`
        
    - Who has access?
    
        - contributor and above
        
    - Who sees what?
    
        - contributor and above sees all
        
        
        
        
## `document_markup`

    - Who has access?
    
        - worker and above
        
    - who sees what?
    
        - worker and above seels all
        
        
        
## `markup_reference`

    - Who has access?
    
        - Public (log in required + permission assignment)
        
    - Who sees what?
    
        - Public and up see everything.
        
        
## `search`

    - Who has access?
    
        - all (no log in)
