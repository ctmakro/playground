var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator.throw(value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments)).next());
    });
};
var wait1s = function () {
    return new Promise(function (resolve) { return setTimeout(resolve, 1000); });
};
function waitfor() {
    return __awaiter(this, void 0, void 0, function* () {
        for (var i = 0; i < 5; i++) {
            yield wait1s();
            console.log(i);
        }
    });
}
yield waitfor();
yield waitfor();
