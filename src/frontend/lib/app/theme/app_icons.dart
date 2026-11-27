import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// Unified stroke-consistent icon set (`LucideIcons`, ~1.75px editorial line)
/// matching SweepFood's botanical design tokens.
abstract final class AppIcons {
  // Navigation
  static const home = LucideIcons.house;
  static const pantry = LucideIcons.refrigerator;
  static const suggestions = LucideIcons.chefHat;
  static const shopping = LucideIcons.shoppingBasket;
  static const profile = LucideIcons.user;

  // Actions & chrome
  static const add = LucideIcons.plus;
  static const minus = LucideIcons.minus;
  static const close = LucideIcons.x;
  static const search = LucideIcons.search;
  static const filter = LucideIcons.slidersHorizontal;
  static const sort = LucideIcons.arrowUpDown;
  static const history = LucideIcons.history;
  static const bell = LucideIcons.bell;
  static const chevronRight = LucideIcons.chevronRight;
  static const chevronLeft = LucideIcons.chevronLeft;
  static const chevronDown = LucideIcons.chevronDown;
  static const check = LucideIcons.check;
  static const checkCircle = LucideIcons.circleCheck;
  static const edit = LucideIcons.pencil;
  static const trash = LucideIcons.trash2;
  static const undo = LucideIcons.undo2;
  static const refresh = LucideIcons.refreshCw;
  static const info = LucideIcons.info;
  static const shield = LucideIcons.shieldCheck;
  static const warning = LucideIcons.triangleAlert;
  static const calendar = LucideIcons.calendar;
  static const clock = LucideIcons.clock;
  static const timer = LucideIcons.timer;

  // Culinary & Kitchen
  static const leaf = LucideIcons.leaf;
  static const cook = LucideIcons.cookingPot;
  static const chefHat = LucideIcons.chefHat;
  static const utensils = LucideIcons.utensils;
  static const flame = LucideIcons.flame;
  static const snowflake = LucideIcons.snowflake;
  static const archive = LucideIcons.package;
  static const scale = LucideIcons.scale;
  static const heart = LucideIcons.heart;
  static const bookmark = LucideIcons.bookmark;
  static const sun = LucideIcons.sun;
  static const moon = LucideIcons.moon;
  static const coffee = LucideIcons.coffee;

  // Auth & form fields (same Lucide stroke family as rest of app)
  static const arrowLeft = LucideIcons.arrowLeft;
  static const arrowRight = LucideIcons.arrowRight;
  static const phone = LucideIcons.phone;
  static const lock = LucideIcons.lock;
  static const mail = LucideIcons.mail;
  static const eye = LucideIcons.eye;
  static const eyeOff = LucideIcons.eyeOff;
  static const messageCode = LucideIcons.messageSquareCode;
  static const star = LucideIcons.star;
  static const award = LucideIcons.award;
  static const globe = LucideIcons.globe;
  static const logOut = LucideIcons.logOut;
  static const smartphone = LucideIcons.smartphone;
  static const trendingUp = LucideIcons.trendingUp;
  static const bookOpen = LucideIcons.bookOpen;
  static const moreVertical = LucideIcons.ellipsisVertical;
  static const arrowLeftRight = LucideIcons.arrowLeftRight;
  static const users = LucideIcons.users;
  static const heartPulse = LucideIcons.heartPulse;
  static const ruler = LucideIcons.ruler;
  static const crown = LucideIcons.crown;
  static const shieldAlert = LucideIcons.shieldAlert;
  static const bellOff = LucideIcons.bellOff;
  static const egg = LucideIcons.egg;
  static const sprout = LucideIcons.sprout;
  static const circle = LucideIcons.circle;
  static const square = LucideIcons.square;
  static const checkSquare = LucideIcons.squareCheck;
  static const lightbulb = LucideIcons.lightbulb;
  static const flashlight = LucideIcons.flashlight;
  static const flashlightOff = LucideIcons.flashlightOff;
  static const image = LucideIcons.image;
  static const cameraOff = LucideIcons.cameraOff;
  static const badgeCheck = LucideIcons.badgeCheck;
  static const packagePlus = LucideIcons.packagePlus;

  // Multimodal capture
  static const camera = LucideIcons.camera;
  static const scan = LucideIcons.scanLine;
  static const mic = LucideIcons.mic;
  static const keyboard = LucideIcons.keyboard;
  static const receipt = LucideIcons.receiptText;

  static IconData forTier(StorageTier tier) => switch (tier) {
    StorageTier.eatSoon => LucideIcons.flame,
    StorageTier.fridge => LucideIcons.refrigerator,
    StorageTier.freezer => LucideIcons.snowflake,
    StorageTier.pantryShelf => LucideIcons.package,
  };

  static IconData forCategory(String rawCategory, {String? fallbackName}) {
    IconData? match(String raw) {
      final c = raw.trim().toLowerCase();
      if (c.isEmpty) return null;
      if (c.contains('trứng') || c.contains('egg')) return LucideIcons.egg;
      if (c.contains('sữa') || c.contains('phô mai') || c.contains('dairy')) {
        return LucideIcons.milk;
      }
      if (c.contains('cá') ||
          c.contains('tôm') ||
          c.contains('mực') ||
          c.contains('hải sản') ||
          c.contains('fish') ||
          c.contains('seafood')) {
        return LucideIcons.fish;
      }
      if (c.contains('thịt') ||
          c.contains('heo') ||
          c.contains('lợn') ||
          c.contains('bò') ||
          c.contains('gà') ||
          c.contains('vịt') ||
          c.contains('meat') ||
          c.contains('pork') ||
          c.contains('beef') ||
          c.contains('chicken')) {
        return LucideIcons.beef;
      }
      if (c.contains('rau') ||
          c.contains('cải') ||
          c.contains('hành') ||
          c.contains('nấm') ||
          c.contains('veg')) {
        return LucideIcons.sprout;
      }
      if (c.contains('trái') ||
          c.contains('củ') ||
          c.contains('cà chua') ||
          c.contains('khoai') ||
          c.contains('fruit')) {
        return LucideIcons.apple;
      }
      if (c.contains('ngũ cốc') ||
          c.contains('gạo') ||
          c.contains('mì') ||
          c.contains('bún') ||
          c.contains('grain')) {
        return LucideIcons.wheat;
      }
      if (c.contains('gia vị') ||
          c.contains('dầu') ||
          c.contains('mắm') ||
          c.contains('spice')) {
        return LucideIcons.flaskConical;
      }
      if (c.contains('đạm')) return LucideIcons.egg;
      return null;
    }

    return match(rawCategory) ??
        (fallbackName != null ? match(fallbackName) : null) ??
        LucideIcons.leaf;
  }
}
