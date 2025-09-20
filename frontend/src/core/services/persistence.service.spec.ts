import { TestBed } from '@angular/core/testing';
import { PersistenceService, ListNavigationState } from './persistence.service';

describe('PersistenceService', () => {
  let service: PersistenceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PersistenceService);

    // Nettoyer les storages avant chaque test
    localStorage.clear();
    sessionStorage.clear();
  });

  afterEach(() => {
    // Nettoyer après chaque test
    localStorage.clear();
    sessionStorage.clear();
  });

  describe('Persistent Data (localStorage)', () => {
    it('should save and retrieve persistent data', () => {
      // Arrange
      const testData = { name: 'test', value: 123 };

      // Act
      service.savePersistent('testKey', testData);
      const retrieved = service.getPersistent<typeof testData>('testKey');

      // Assert
      expect(retrieved).toEqual(testData);
    });

    it('should return null for non-existent persistent data', () => {
      // Act
      const retrieved = service.getPersistent('nonExistent');

      // Assert
      expect(retrieved).toBeNull();
    });

    it('should remove persistent data', () => {
      // Arrange
      service.savePersistent('testKey', 'test value');

      // Act
      service.removePersistent('testKey');
      const retrieved = service.getPersistent('testKey');

      // Assert
      expect(retrieved).toBeNull();
    });

    it('should manage active group ID', () => {
      // Act
      service.saveActiveGroupId(42);
      const groupId = service.getActiveGroupId();

      // Assert
      expect(groupId).toBe(42);
    });

    it('should manage user preferences', () => {
      // Act
      service.saveUserPreference('theme', 'dark');
      const theme = service.getUserPreference<string>('theme');

      // Assert
      expect(theme).toBe('dark');
    });
  });

  describe('Navigation State (sessionStorage)', () => {
    it('should save and retrieve navigation state', () => {
      // Arrange
      const state: ListNavigationState = {
        currentPage: 3,
        pageSize: 25,
        filters: { status: 'active' },
        sortBy: 'name',
        scrollPosition: 500
      };

      // Act
      service.saveNavigationState('test-component', state);
      const retrieved = service.getNavigationState<ListNavigationState>('test-component');

      // Assert
      expect(retrieved).toEqual(state);
    });

    it('should return null for expired navigation state', () => {
      // Arrange
      const state = { currentPage: 1, pageSize: 25 };

      // Act
      service.saveNavigationState('test-component', state);
      const retrieved = service.getNavigationState('test-component', 0); // maxAge = 0 = expired

      // Assert
      expect(retrieved).toBeNull();
    });

    it('should use list state helper methods', () => {
      // Arrange
      const listState: ListNavigationState = {
        currentPage: 2,
        pageSize: 50,
        filters: { category: 'gifts' }
      };

      // Act
      service.saveListState('gift-list', listState);
      const retrieved = service.getListState('gift-list');

      // Assert
      expect(retrieved).toEqual(listState);
    });
  });

  describe('Cleanup Operations', () => {
    it('should clear all persistent data', () => {
      // Arrange
      service.savePersistent('key1', 'value1');
      service.savePersistent('key2', 'value2');
      service.saveActiveGroupId(123);

      // Act
      service.clearAllPersistent();

      // Assert
      expect(service.getPersistent('key1')).toBeNull();
      expect(service.getPersistent('key2')).toBeNull();
      expect(service.getActiveGroupId()).toBeNull();
    });

    it('should clear all navigation states', () => {
      // Arrange
      service.saveNavigationState('comp1', { data: 'test1' });
      service.saveNavigationState('comp2', { data: 'test2' });

      // Act
      service.clearAllNavigationStates();

      // Assert
      expect(service.getNavigationState('comp1')).toBeNull();
      expect(service.getNavigationState('comp2')).toBeNull();
    });

    it('should not interfere with other localStorage data', () => {
      // Arrange
      localStorage.setItem('other_app.data', 'should not be removed');
      service.savePersistent('our_data', 'should be removed');

      // Act
      service.clearAllPersistent();

      // Assert
      expect(localStorage.getItem('other_app.data')).toBe('should not be removed');
      expect(service.getPersistent('our_data')).toBeNull();
    });
  });

  describe('Error Handling', () => {
    it('should handle localStorage quota exceeded gracefully', () => {
      // Arrange
      const originalSetItem = localStorage.setItem;
      spyOn(localStorage, 'setItem').and.throwError('QuotaExceededError');

      // Act & Assert
      expect(() => service.savePersistent('test', 'data')).not.toThrow();

      // Cleanup
      localStorage.setItem = originalSetItem;
    });

    it('should handle corrupted localStorage data gracefully', () => {
      // Arrange
      localStorage.setItem('app_kdo.corrupted', 'invalid json {');

      // Act & Assert
      expect(() => service.getPersistent('corrupted')).not.toThrow();
      expect(service.getPersistent('corrupted')).toBeNull();
    });
  });
});