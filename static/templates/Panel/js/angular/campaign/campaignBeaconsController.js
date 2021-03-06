angular.module('panelApp').controller('campaignBeaconsController', ['$routeParams', 'CampaignBeacons', 'CampaignBeacon', 'currentPath', 'toast', 'campaignMENU', 'panelCache', 'CampaignBeaconsGenerate', 'pageLoader', function($routeParams, CampaignBeacons, CampaignBeacon, currentPath, toast, campaignMENU, panelCache, CampaignBeaconsGenerate, pageLoader){
    // lock
    this.isLock = false;
    this.lock = function(){
        this.isLock = true;
    }
    this.unlock = function(){
        this.isLock = false;
    }
    // api info
    this.currentPath = currentPath;
    this.toast = toast;
    this.cache = panelCache;
    // campaign params
    this.id = $routeParams.campaignID;
    this.campaignM = campaignMENU;
    this.campaignM.setID(this.id>0?this.id:0);
    // models
    this.beaconsList = [];
    this.beaconsPages = [];	// numbers
    this.perPage = 5;
    this.beaconsCurrentPage = 1;
    this.numberOfBeaconsItems = 0;
    // nav
    this.beaconsNavActive = function(page){
        if (page==this.beaconsCurrentPage){
            return "active"
        } else {
            return "";
        }
    };
    this.beaconsNavNext = function(){
        if (this.beaconsCurrentPage<this.beaconsPages.length){
            this.getBeacons(this.beaconsCurrentPage+1);
        }
    };
    this.beaconsNavPrev = function(){
        if (this.beaconsCurrentPage>1){
            this.getBeacons(this.beaconsCurrentPage-1);
        }
    };

    this.updatePath = function () {
        this.currentPath.setPath("Campaign / " + this.cache.getCampaignName(this.id) + " / Beacons");
        this.currentPath.setPage("Beacons");
    }
    // api
    this.getBeacons = function(page){
        if (this.isLock){
            return;
        } else {
            this.lock();
        }

        pageLoader.showLoader();

        CampaignBeacons.get({campaignID:this.id, page:page, pagination:true}, function(success){
            this.beaconsList = [];
            this.beaconsPages = [];
            this.beaconsList = success.results;
            this.numberOfBeaconsItems = success.count;
            for (var i=0; i<Math.ceil((this.numberOfBeaconsItems/this.perPage)); i++) {
                this.beaconsPages.push(i+1);
            }
            this.beaconsCurrentPage = page;
            this.unlock();
            pageLoader.hideLoader();
        }.bind(this), function(error){
            this.toast.showApiError(error);
            this.unlock();
            pageLoader.hideLoader();
        }.bind(this));

    };
    this.deleteBeacon = function(beaconID){
        if (this.isLock){
            return;
        } else {
            this.lock();
        };

        CampaignBeacon.delete({campaignID:this.id, beaconID:beaconID}, function(){
            this.numberOfItems = this.numberOfItems - 1;
            if ( (this.numberOfItems <= (this.beaconsCurrentPage-1) * this.perPage) && this.numberOfItems>=this.perPage ){
                this.beaconsCurrentPage = this.beaconsCurrentPage - 1;
            }
            this.unlock();
            this.getBeacons(this.beaconsCurrentPage);
            this.toast.showSuccess();
        }.bind(this), function(error){
            this.unlock();
            this.toast.showApiError(error);
        }.bind(this));
    }

    this.generateBeacons = function(){
        if (this.isLock){
            return;
        } else {
            this.lock();
        }

        CampaignBeaconsGenerate.save({campaignID:this.id}, {count:this.numberOfNewBeacons}, function(){
            this.unlock();
            this.getBeacons(this.beaconsCurrentPage);
            this.toast.showSuccess();
        }.bind(this), function(error){
            this.unlock();
            this.toast.showApiError(error);
        }.bind(this))

    }

    this.getBeacons(1);
    this.updatePath();

}]);