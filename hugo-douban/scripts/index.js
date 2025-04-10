/**
 * Created by myths on 18-2-8.
 */

Element.prototype.siblings = function () {
    var siblingElement = [];
    var sibs = this.parentNode.children;
    for (var i = 0; i < sibs.length; i++) {
        if (sibs[i] !== this) {
            siblingElement.push(sibs[i]);
        }
    }
    return siblingElement;
};
